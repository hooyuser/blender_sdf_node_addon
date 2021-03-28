import bpy
import bgl
import gpu
from gpu_extras.batch import batch_for_shader
import math
import mathutils
# import inspect
from bpy_extras import view3d_utils

from .node_parser import NodeList


def render_size(scene):
    render = scene.render
    percent = render.resolution_percentage * 0.01
    dim_x = round(render.resolution_x * percent)
    dim_y = round(render.resolution_y * percent)
    return round(dim_x), round(dim_y)


class Draw(object):
    handlers = []
    config = {"size": [0, 0]}

    v_ = '''
    in vec2 pos;
    out vec2 position;
    uniform mat4 ModelViewProjectionMatrix;

    void main()
    {
        position = pos;
        gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
    }
    '''

    f_1 = '''
    in vec2 position;
    out vec4 fragColor;
    uniform mat4 PersInv;
    uniform mat4 ViewInv;
    uniform vec3 CamLoc;
    uniform vec3 LightLoc;
    uniform vec2 Size;
    uniform bool IsPers;

    #define PI 3.1415926535
    #define EPSILON 0.0001
    #define UPPER 0.9999
    #define MAX_MARCHING_STEPS 300
    #define MIN_DIST 0.0
    #define MAX_DIST 800.0

    uint hash( uint x ) {
                    x += ( x << 10u );
                    x ^= ( x >>  6u );
                    x += ( x <<  3u );
                    x ^= ( x >> 11u );
                    x += ( x << 15u );
                    return x;
                }

    uint hash( uvec2 v ) { return hash( v.x ^ hash(v.y)                         ); }
    uint hash( uvec3 v ) { return hash( v.x ^ hash(v.y) ^ hash(v.z)             ); }
    uint hash( uvec4 v ) { return hash( v.x ^ hash(v.y) ^ hash(v.z) ^ hash(v.w) ); }

    float floatConstruct( uint m ) {
        const uint ieeeMantissa = 0x007FFFFFu; // binary32 mantissa bitmask
        const uint ieeeOne      = 0x3F800000u; // 1.0 in IEEE binary32

        m &= ieeeMantissa;                     // Keep only mantissa bits (fractional part)
        m |= ieeeOne;                          // Add fractional part to 1.0

        float  f = uintBitsToFloat( m );       // Range [1:2]
        return f - 1.0;                        // Range [0:1]
    }

    float random( float x ) { return floatConstruct(hash(floatBitsToUint(x))); }
    float random( vec2  v ) { return floatConstruct(hash(floatBitsToUint(v))); }
    float random( vec3  v ) { return floatConstruct(hash(floatBitsToUint(v))); }
    float random( vec4  v ) { return floatConstruct(hash(floatBitsToUint(v))); }


    //////////////////////////////////////////////////////////////////
    //4D Simplex noise
    //////////////////////////////////////////////////////////////////

    vec4 mod289(vec4 x) {
    return x - floor(x * (1.0 / 289.0)) * 289.0;
    }

    float mod289(float x) {
        return x - floor(x * (1.0 / 289.0)) * 289.0;
    }

    vec4 permute(vec4 x) {
        return mod289(((x*34.0)+1.0)*x);
    }

    float permute(float x) {
        return mod289(((x*34.0)+1.0)*x);
    }

    vec4 taylorInvSqrt(vec4 r) {
        return 1.79284291400159 - 0.85373472095314 * r;
    }

    float taylorInvSqrt(float r) {
        return 1.79284291400159 - 0.85373472095314 * r;
    }

    vec4 grad4(float j, vec4 ip) {
        const vec4 ones = vec4(1.0, 1.0, 1.0, -1.0);
        vec4 p,s;

        p.xyz = floor( fract (vec3(j) * ip.xyz) * 7.0) * ip.z - 1.0;
        p.w = 1.5 - dot(abs(p.xyz), ones.xyz);
        s = vec4(lessThan(p, vec4(0.0)));
        p.xyz = p.xyz + (s.xyz*2.0 - 1.0) * s.www;

        return p;
    }

    // (sqrt(5) - 1)/4 = F4, used once below
    #define F4 0.309016994374947451

    //////////////////////////////////////////////////////////////////
    // 3D Value Noise
    //////////////////////////////////////////////////////////////////

    float hash1(float n) {
        return fract( n*17.0*fract( n*0.3183099 ) );
    }

    // Taken from Inigo Quilez's Rainforest ShaderToy:
    // https://www.shadertoy.com/view/4ttSWf
    float valueNoise3D(in vec3 x)
    {
        vec3 p = floor(x);
        vec3 w = fract(x);

        vec3 u = w*w*w*(w*(w*6.0-15.0)+10.0);

        float n = p.x + 317.0*p.y + 157.0*p.z;

        float a = hash1(n+0.0);
        float b = hash1(n+1.0);
        float c = hash1(n+317.0);
        float d = hash1(n+318.0);
        float e = hash1(n+157.0);
        float f = hash1(n+158.0);
        float g = hash1(n+474.0);
        float h = hash1(n+475.0);

        float k0 =   a;
        float k1 =   b - a;
        float k2 =   c - a;
        float k3 =   e - a;
        float k4 =   a - b - c + d;
        float k5 =   a - c - e + g;
        float k6 =   a - b - e + f;
        float k7 = - a + b + c - d + e - f - g + h;

        return -1.0+2.0*(k0 + k1*u.x + k2*u.y + k3*u.z + k4*u.x*u.y + k5*u.y*u.z + k6*u.z*u.x + k7*u.x*u.y*u.z);
    }

    const mat3 m3  = mat3( 0.00,  0.80,  0.60,
                        -0.80,  0.36, -0.48,
                        -0.60, -0.48,  0.64 );

    //////////////////////////////////////////////////////////////////
    // 3D Simplex Noise
    //////////////////////////////////////////////////////////////////
    vec3 random3(vec3 c) {
        float j = 4096.0*sin(dot(c,vec3(17.0, 59.4, 15.0)));
        vec3 r;
        r.z = fract(512.0*j);
        j *= .125;
        r.x = fract(512.0*j);
        j *= .125;
        r.y = fract(512.0*j);
        return r-0.5;
    }

    /* skew constants for 3d simplex functions */
    const float F3 =  0.3333333;
    const float G3 =  0.1666667;

    /* 3d simplex noise */
    float simplexNoise3D(vec3 p) {
        /* 1. find current tetrahedron T and it's four vertices */
        /* s, s+i1, s+i2, s+1.0 - absolute skewed (integer) coordinates of T vertices */
        /* x, x1, x2, x3 - unskewed coordinates of p relative to each of T vertices*/

        /* calculate s and x */
        vec3 s = floor(p + dot(p, vec3(F3)));
        vec3 x = p - s + dot(s, vec3(G3));

        /* calculate i1 and i2 */
        vec3 e = step(vec3(0.0), x - x.yzx);
        vec3 i1 = e*(1.0 - e.zxy);
        vec3 i2 = 1.0 - e.zxy*(1.0 - e);

        /* x1, x2, x3 */
        vec3 x1 = x - i1 + G3;
        vec3 x2 = x - i2 + 2.0*G3;
        vec3 x3 = x - 1.0 + 3.0*G3;

        /* 2. find four surflets and store them in d */
        vec4 w, d;

        /* calculate surflet weights */
        w.x = dot(x, x);
        w.y = dot(x1, x1);
        w.z = dot(x2, x2);
        w.w = dot(x3, x3);

        /* w fades from 0.6 at the center of the surflet to 0.0 at the margin */
        w = max(0.6 - w, 0.0);

        /* calculate surflet components */
        d.x = dot(random3(s), x);
        d.y = dot(random3(s + i1), x1);
        d.z = dot(random3(s + i2), x2);
        d.w = dot(random3(s + 1.0), x3);

        /* multiply d by w^4 */
        w *= w;
        w *= w;
        d *= w;

        /* 3. return the sum of the four surflets */
        return dot(d, vec4(52.0));
    }
    '''

    f_2 = '''
    float sceneSDF(vec3 p)
    {
    '''

    f_3 = '''
    }

    vec3 calcNormal(vec3  p) { // for function f(p)
        const float h = 0.0001;// replace by an appropriate value
        const vec2 k = vec2(1, -1);
        return normalize(k.xyy*sceneSDF(p + k.xyy*h) +
        k.yyx*sceneSDF(p + k.yyx*h) +
        k.yxy*sceneSDF(p + k.yxy*h) +
        k.xxx*sceneSDF(p + k.xxx*h));
    }

    float shortestDistanceToSurface(
        vec3 eye, vec3 marchingDirection, float start, float end)
    {
        float depth = start;
        for (int i = 0; i < MAX_MARCHING_STEPS; i++)
        {
            float dist = sceneSDF(eye + depth * marchingDirection);
            if (dist < EPSILON)
            {
                return depth;
            }
            depth += dist;
            if (depth >= end)
            {
                return end;
            }
        }
        return end;
    }

    vec4 objectPBRLighting(vec3 p, vec3 v){
        vec3 baseColor = vec3(0.8,0.7,0.9);
        float metalness = 0.0;
        float roughness = 0.5;
        float specular = 0.5;

        vec3 n = calcNormal(p);

        vec3 light = 200.0 * normalize(LightLoc);
        vec3 light_color = 0.04 * vec3(1.0,1.0,1.0);

        //float falloffLength = dot(light - p, light - p);
        //l: vector from sample point to light
        vec3 l = normalize(light - p);
        //h: normal vector of the microface at the sample point
        vec3 h = normalize(v + l);
        float a = roughness * roughness;
        float dotNL = clamp (dot (n, l), EPSILON, UPPER);
        float dotNV = clamp (dot (n, v), EPSILON, UPPER);
        float dotNH = clamp (dot (n, h), EPSILON, UPPER);
        float dotHV = clamp (dot (l, h), EPSILON, UPPER);

        float d = (dotNH * a * a - dotNH) * dotNH + 1.;
        float D = a * a / (PI * d * d);//GGX
        float Vis_SmithV = dotNL * (dotNV * (1. - a) + a);
        float Vis_SmithL = dotNV * (dotNL * (1. - a) + a);
        // VIS = G / (4. * dotNV * dotNL)
        float Vis = 0.5 / (Vis_SmithV + Vis_SmithL);
        vec3 F0 = mix(vec3(0.16 * specular * specular), baseColor, metalness);
        vec3 F = F0 + (1. - F0) * (1. - dotHV) * (1. - dotHV)
            * (1. - dotHV) * (1. - dotHV) * (1. - dotHV);
        vec3 kD = (1. - F) * (1. - metalness);
        vec3 f = kD * baseColor / PI + F * D * Vis;
        vec3 c = PI * f * light_color * dotNL * 17. + vec3(0.15);
        return vec4(c,1.0);
    }

    vec3 rayDirection(vec2 fragCoord)
    {
        if (IsPers)
        {
            vec3 outer = vec3((2.0 * fragCoord.x / Size.x) - 1.0,
                            (2.0 * fragCoord.y / Size.y) - 1.0,
                            -0.5);
            float w = dot(outer, PersInv[3].xyz) + PersInv[3][3];
            return normalize((((vec4(outer, 1.0) * PersInv).xyz / w)
                - vec3(ViewInv[0][3],ViewInv[1][3],ViewInv[2][3])));
        }
        else
        {
            return - normalize(vec3(ViewInv[0][2],ViewInv[1][2],ViewInv[2][2]));
        }
    }


    void main()
    {
        vec3 dir = rayDirection(position);
        float dist = shortestDistanceToSurface(CamLoc, dir,
            MIN_DIST, MAX_DIST);

        if (dist > MAX_DIST - EPSILON) {
            // Didn't hit anything
            fragColor = vec4(0.0, 0.0, 0.0, 0.0);
            fragColor = blender_srgb_to_framebuffer_space(fragColor);
            return;
        }

        vec3 p = CamLoc + dist * dir;

        fragColor = objectPBRLighting(p, -dir);
        fragColor = blender_srgb_to_framebuffer_space(fragColor);
    }
    '''

    @classmethod
    def rot(cls, vec, dtheta, dphi):
        x = vec[0]
        y = vec[1]
        z = vec[2]
        r = math.sqrt(x * x + y * y + z * z)
        theta = math.atan2(y, x) + dtheta * math.pi / 180
        phi = math.acos(z / r) + dphi * math.pi / 180  # to degrees
        return (math.sin(phi) * math.cos(theta),
                math.sin(phi) * math.sin(theta), math.cos(phi))

    @classmethod
    def update_config(cls):
        screen = bpy.context.window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region3d = area.spaces[0].region_3d
                        cls.config["size"] = [region.width, region.height]
                        inv_pers = region3d.perspective_matrix.inverted()
                        cls.config["inv_pers_matrix"] = inv_pers.transposed()
                        inv_view = region3d.view_matrix.inverted()
                        cls.config["inv_view_matrix"] = inv_view.transposed()
                        cls.config["is_perspective"] = region3d.is_perspective
                        if cls.config["is_perspective"]:
                            cls.config["cam"] = inv_view.translation
                        else:
                            cls.config[
                                "cam"] = view3d_utils.region_2d_to_origin_3d(
                                    region,
                                    region3d,
                                    [region.width / 2, region.height / 2],
                                    clamp=10.0)

                        cls.config["light"] = mathutils.Vector(
                            cls.rot(cls.config["cam"], 30, -30))

    indices = ((0, 1, 2), (2, 1, 3))

    @classmethod
    def tag_redraw_all_3dviews(cls):
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            region.tag_redraw()

    @classmethod
    def render(cls, context):
        IMAGE_NAME = "Generated Image"

        render = context.scene.render  # bpy.data.scenes['Scene'].render
        percent = render.resolution_percentage * 0.01
        WIDTH = round(render.resolution_x * percent)
        HEIGHT = round(render.resolution_y * percent)

        offscreen = gpu.types.GPUOffScreen(WIDTH, HEIGHT)

        screen = bpy.context.window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region3d = area.spaces[0].region_3d
                        w_matrix = region3d.window_matrix.copy()
                        v_matrix = region3d.view_matrix
        if w_matrix[1][1] / w_matrix[0][0] > WIDTH / HEIGHT:
            w_matrix[1][1] = w_matrix[0][0] * WIDTH / HEIGHT
        else:
            w_matrix[0][0] = w_matrix[1][1] * HEIGHT / WIDTH
        inv_pers = (w_matrix @ v_matrix).inverted().transposed()

        with offscreen.bind():
            bgl.glClearColor(0.2, 0.2, 0.2, 1.0)
            bgl.glClear(bgl.GL_COLOR_BUFFER_BIT)

            version = bgl.glGetString(bgl.GL_VERSION)
            print(version)
            with gpu.matrix.push_pop():
                # reset matrices -> use normalized device coordinates [-1, 1]
                # gpu.matrix.load_matrix(mathutils.Matrix.Identity(4))

                vertices = ((0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT))

                indices = ((0, 1, 2), (2, 1, 3))

                shader = gpu.types.GPUShader(
                    cls.v_, cls.f_1 + cls.glsl_nodes.glsl_func_text + cls.f_2 +
                    cls.glsl_nodes.glsl_sdf_text + cls.f_3)
                shader.bind()
                # cls.update_config()
                shader.uniform_float("ViewInv", cls.config["inv_view_matrix"])

                shader.uniform_float("PersInv", inv_pers)
                shader.uniform_float("Size", (WIDTH, HEIGHT))
                shader.uniform_float("CamLoc", cls.config["cam"])
                shader.uniform_float("LightLoc", cls.config["light"])
                shader.uniform_bool("IsPers", (cls.config["is_perspective"], ))

                batch = batch_for_shader(shader,
                                         'TRIS', {"pos": vertices},
                                         indices=indices)

                projection_matrix = mathutils.Matrix.Diagonal(
                    (2.0 / WIDTH, 2.0 / HEIGHT, 1))
                projection_matrix = mathutils.Matrix.Translation(
                    (-1.0, -1.0, 0.0)) @ projection_matrix.to_4x4()
                gpu.matrix.load_projection_matrix(projection_matrix)

                batch.draw(shader)

            buffer = bgl.Buffer(bgl.GL_FLOAT, WIDTH * HEIGHT * 4)
            bgl.glReadBuffer(bgl.GL_BACK)
            bgl.glReadPixels(0, 0, WIDTH, HEIGHT, bgl.GL_RGBA, bgl.GL_FLOAT,
                             buffer)

        offscreen.free()

        if IMAGE_NAME not in bpy.data.images:
            bpy.data.images.new(IMAGE_NAME, WIDTH, HEIGHT)
        image = bpy.data.images[IMAGE_NAME]
        image.scale(WIDTH, HEIGHT)
        image.pixels.foreach_set(buffer)

    glsl_nodes = NodeList()

    @classmethod
    def gen_draw_handler(cls, update_node=False):

        if update_node:
            cls.glsl_nodes.update_glsl_func(update_node)
        else:
            cls.glsl_nodes.gen_node_list(
                bpy.context.space_data.edit_tree.nodes[
                    bpy.context.scene.sdf_node_data.active_viewer])
        # print('GLSL:\n')
        # print(cls.glsl_nodes.glsl_func_text)
        # print(cls.glsl_nodes.glsl_sdf_text)

        cls.shader = gpu.types.GPUShader(
            cls.v_, cls.f_1 + cls.glsl_nodes.glsl_func_text + cls.f_2 +
            cls.glsl_nodes.glsl_sdf_text + cls.f_3)

        def draw():
            bgl.glEnable(bgl.GL_BLEND)
            cls.shader.bind()
            cls.update_config()
            [width, height] = cls.config["size"]
            cls.shader.uniform_float("ViewInv", cls.config["inv_view_matrix"])
            cls.shader.uniform_float("PersInv", cls.config["inv_pers_matrix"])
            cls.shader.uniform_float("Size", (width, height))
            cls.shader.uniform_float("CamLoc", cls.config["cam"])
            cls.shader.uniform_float("LightLoc", cls.config["light"])
            cls.shader.uniform_bool("IsPers", (cls.config["is_perspective"], ))
            vertices = ((0, 0), (width, 0), (0, height), (width, height))
            batch = batch_for_shader(cls.shader,
                                     'TRIS', {"pos": vertices},
                                     indices=cls.indices)
            batch.draw(cls.shader)

        return draw

    @classmethod
    def refreshViewport(cls, enabled_show, update_node=False):
        if enabled_show:
            if len(cls.handlers) == 0:
                cls.handlers.append(
                    bpy.types.SpaceView3D.draw_handler_add(
                        cls.gen_draw_handler(update_node), (), 'WINDOW',
                        'POST_PIXEL'))
                cls.tag_redraw_all_3dviews()
        else:
            if cls.handlers:
                bpy.types.SpaceView3D.draw_handler_remove(
                    cls.handlers[0], 'WINDOW')
                del cls.handlers[0]
                cls.tag_redraw_all_3dviews()

    @classmethod
    def update_callback(cls, update_node=False):
        if update_node and update_node.index <= -2:  # update_node is math node
            update_node.update()
        elif update_node and update_node.index < 0:
            return
        else:
            nodetree = update_node.id_data if update_node else bpy.context.space_data.edit_tree
            for node in nodetree.nodes:
                if node.bl_idname == 'Viewer':
                    # print('has Viewer')
                    if node.enabled_show and node.inputs[0].links:
                        cls.refreshViewport(False, update_node)
                        cls.refreshViewport(True, update_node)
