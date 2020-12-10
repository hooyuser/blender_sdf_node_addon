import bpy
import bgl
import gpu
from gpu_extras.batch import batch_for_shader
import math
import mathutils
# import inspect
from bpy_extras import view3d_utils


class NodeList(object):

    tree = None

    def __init__(self):
        self.reset()

    def reset(self):
        self.node_list = []
        self.ref_stacks = []
        self.glsl_func_list = []
        self.glsl_p_list = []
        self.glsl_d_list = []
        self.glsl_func_text = ''
        self.glsl_sdf_text = ''

    def gen_node_info(self, node_in):
        for node in self.tree.nodes:
            node.index = -1
            node.ref_num = 0
        self.followLinks(node_in)

    def gen_node_list(self, node_in):
        self.reset()
        self.tree = bpy.context.space_data.edit_tree
        self.gen_node_info(node_in)
        if self.node_list:
            num = len(self.node_list) - 1
            ref_n = self.node_list[num].ref_num

            for node in self.node_list:
                self.glsl_func_list.append(node.gen_glsl_func())
            self.glsl_p_list.reverse()

            self.glsl_sdf_text = f'''
            vec3 p_{num}_{ref_n} = p;
            ''' + ''.join(self.glsl_p_list) + ''.join(self.glsl_d_list) + f'''
            return d_{num}_{ref_n};
            '''
            self.glsl_func_text = ''.join(self.glsl_func_list)
            # inspect.cleandoc(self.glsl_sdf_text)

        else:
            self.glsl_sdf_text = 'return 2 * MAX_DIST;'

    def update_glsl_func(self, node):
        if self.node_list:
            self.glsl_func_list[node.index] = node.gen_glsl_func()
            self.glsl_func_text = ''.join(self.glsl_func_list)
            # inspect.cleandoc(self.glsl_sdf_text)

    def followLinks(self, node_in):

        for n_inputs in node_in.inputs:
            for node_link in n_inputs.links:
                to_name = node_link.to_socket.bl_idname
                if node_link.from_socket.bl_idname == to_name:
                    node = node_link.from_node
                    self.followLinks(node)

                    if node.index < 0:
                        node.index = len(self.node_list)
                        self.node_list.append(node)
                        self.ref_stacks.append([0])
                    else:
                        node.ref_num += 1
                        self.ref_stacks[node.index].append(node.ref_num)

                    # print(node.name, ':', node.index, node.ref_num)
                    glsl = node.gen_glsl(self.ref_stacks)
                    self.glsl_p_list.append(glsl[0])
                    self.glsl_d_list.append(glsl[1])


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
    #define EPSILON 0.001
    #define UPPER 0.9999
    #define MAX_MARCHING_STEPS 200
    #define MIN_DIST 0.0
    #define MAX_DIST 800.0
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

                        # print(cls.config["is_perspective"], cls.config["cam"])

                        # print((-inv_view.col[2].xyz).normalized())

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
        cls.shader.uniform_bool("IsPers", (cls.config["is_perspective"], ))
        vertices = ((0, 0), (width, 0), (0, height), (width, height))
        batch = batch_for_shader(cls.shader,
                                 'TRIS', {"pos": vertices},
                                 indices=cls.indices)
        batch.draw(cls.shader)

    glsl_nodes = NodeList()

    @classmethod
    def gen_draw_handler(cls, update_node=False):

        # class Node_OT_test(Operator):
        # bl_idname = "node.test"
        # bl_label  = "Test"
        # def execute(self, context):
        # selection = context.selected_nodes
        #     print(selection)
        # return {'FINISHED'}

        if update_node:
            cls.glsl_nodes.update_glsl_func(update_node)
        else:
            cls.glsl_nodes.gen_node_list(
                bpy.context.space_data.edit_tree.nodes["Viewer"])
        # print('GLSL:\n')
        # print(cls.glsl_nodes.glsl_func_text)
        # print(cls.glsl_nodes.glsl_sdf_text)

        shader = gpu.types.GPUShader(
            cls.v_, cls.f_1 + cls.glsl_nodes.glsl_func_text + cls.f_2 +
            cls.glsl_nodes.glsl_sdf_text + cls.f_3)

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
            shader.uniform_bool("IsPers", (cls.config["is_perspective"], ))
            vertices = ((0, 0), (width, 0), (0, height), (width, height))
            batch = batch_for_shader(shader,
                                     'TRIS', {"pos": vertices},
                                     indices=cls.indices)
            batch.draw(shader)

        return draw

    @classmethod
    def refreshViewport(cls, enabled, update_node=False):
        if enabled:
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
        if update_node and update_node.index < 0:
            return
        else:
            for node in bpy.context.space_data.edit_tree.nodes:
                if node.bl_idname == 'Viewer':
                    # print('has Viewer')
                    if node.enabled and node.inputs[0].links:
                        cls.refreshViewport(False, update_node)
                        cls.refreshViewport(True, update_node)
