import bpy
import bgl
import gpu
from gpu_extras.batch import batch_for_shader
import math
import mathutils
import inspect
from .addonStatus import Status


class NodeList(object):

    tree = None

    def __init__(self):
        self.node_list = []
        self.glsl_text = ''

    def gen_node_list(self, node_in):
        self.node_list = []
        self.glsl_text = ''
        self.tree = bpy.context.space_data.edit_tree
        for node in self.tree.nodes:
            node.index = -1
        self.followLinks(node_in)
        self.glsl_text += '''
            return d_{};'''.format(len(self.node_list) - 1)
        inspect.cleandoc(self.glsl_text)

    def followLinks(self, node_in):

        for n_inputs in node_in.inputs:
            for node_links in n_inputs.links:
                self.followLinks(node_links.from_node)
                node_name = node_links.from_node.name
                node = self.tree.nodes[node_name]

                if node.index < 0:
                    node.index = len(self.node_list)
                    self.node_list.append(node)
                    print(node.name, ':', node.index)
                    self.glsl_text += node.gen_glsl()


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

    #define PI 3.1415926535
    #define EPSILON 0.001
    #define UPPER 0.9999
    #define MAX_MARCHING_STEPS 200
    #define MIN_DIST 0.0
    #define MAX_DIST 800.0

    float sphereSDF(vec3 samplePoint)
    {
        return length(samplePoint) - 1.0;
    }

    float sceneSDF(vec3 p)
    {
    '''

    f_2 = '''
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
        vec3 outer = vec3((2.0 * fragCoord.x / Size.x) - 1.0,
                        (2.0 * fragCoord.y / Size.y) - 1.0,
                        -0.5);
        float w = dot(outer, PersInv[3].xyz) + PersInv[3][3];
        return normalize((((vec4(outer, 1.0) * PersInv).xyz / w)
            - vec3(ViewInv[0].w,ViewInv[1].w,ViewInv[2].w)));
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
                        cls.config["cam"] = inv_view.translation
                        cls.config["light"] = mathutils.Vector(
                            cls.rot(cls.config["cam"], 30, -30))

    vertices = ((0, 0), (600, 0), (0, 600), (600, 600))

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
    def draw(cls):
        cls.shader.bind()
        cls.update_config()
        [width, height] = cls.config["size"]
        cls.shader.uniform_float("ViewInv", cls.config["inv_view_matrix"])
        cls.shader.uniform_float("PersInv", cls.config["inv_pers_matrix"])
        cls.shader.uniform_float("Size", (width, height))
        cls.shader.uniform_float("CamLoc", cls.config["cam"])
        cls.shader.uniform_float("LightLoc", cls.config["light"])
        vertices = ((0, 0), (width, 0), (0, height), (width, height))
        batch = batch_for_shader(cls.shader,
                                 'TRIS', {"pos": vertices},
                                 indices=cls.indices)
        batch.draw(cls.shader)

    glsl_nodes = NodeList()

    @classmethod
    def gen_draw_handler(cls):

        print('GLSL:\n')
        # nodetree = bpy.data.node_groups[
        # "NodeTree"]   bpy.data.node_groups["NodeTree"].nodes.active   update_tag  interface_update
        # no = nodetree.nodes[
        # "Sphere SDF"]   bpy.data.node_groups["NodeTree"].nodes["Sphere SDF"].socket_value_update()
        # x = no.inputs[0]
        # y = x.default_value
        # print(y)
        # print('active_node', bpy.context.space_data.edit_tree)

        # class Node_OT_test(Operator):
        # bl_idname = "node.test"
        # bl_label  = "Test"
        # def execute(self, context):
        # selection = context.selected_nodes
        #     print(selection)
        # return {'FINISHED'}

        cls.glsl_nodes.gen_node_list(
            bpy.context.space_data.edit_tree.nodes["Viewer"])
        print(cls.glsl_nodes.glsl_text)

        shader = gpu.types.GPUShader(
            cls.v_, cls.f_1 + cls.glsl_nodes.glsl_text + cls.f_2)

        def draw():
            bgl.glEnable(bgl.GL_BLEND)
            shader.bind()
            cls.update_config()
            [width, height] = cls.config["size"]
            shader.uniform_float("ViewInv", cls.config["inv_view_matrix"])
            shader.uniform_float("PersInv", cls.config["inv_pers_matrix"])
            shader.uniform_float("Size", (width, height))
            shader.uniform_float("CamLoc", cls.config["cam"])
            shader.uniform_float("LightLoc", cls.config["light"])
            vertices = ((0, 0), (width, 0), (0, height), (width, height))
            batch = batch_for_shader(shader,
                                     'TRIS', {"pos": vertices},
                                     indices=cls.indices)
            batch.draw(shader)

        return draw

    @classmethod
    def refreshViewport(cls, enabled):
        if enabled:
            if len(cls.handlers) == 0:
                cls.handlers.append(
                    bpy.types.SpaceView3D.draw_handler_add(
                        cls.gen_draw_handler(), (), 'WINDOW', 'POST_PIXEL'))
                cls.tag_redraw_all_3dviews()
        else:
            if cls.handlers:
                bpy.types.SpaceView3D.draw_handler_remove(
                    cls.handlers[0], 'WINDOW')
                del cls.handlers[0]
                cls.tag_redraw_all_3dviews()

    @classmethod
    def every_second(cls):
        if Status.active_nodetree():
            v = bpy.data.node_groups[Status.active_nodetree()].nodes.get(
                "Viewer")
            if v:
                if v.enabled:
                    Draw.refreshViewport(False)
                    Draw.refreshViewport(True)
            return 0.1
