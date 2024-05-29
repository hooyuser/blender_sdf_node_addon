import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import math
import mathutils
# import inspect
from bpy_extras import view3d_utils

from .node_parser import NodeList
from .shaders import shader_base


def render_size(scene):
    render = scene.render
    percent = render.resolution_percentage * 0.01
    dim_x = round(render.resolution_x * percent)
    dim_y = round(render.resolution_y * percent)
    return round(dim_x), round(dim_y)


class Draw(object):
    handlers = []
    config = {"size": [0, 0]}
    glsl_nodes = NodeList()
    indices = ((0, 1, 2), (2, 1, 3))
    frag_shader_code: str

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

                        # cls.config["light"] = mathutils.Vector(
                        #    cls.rot(cls.config["cam"], 30, -30))
        lights = [ob for ob in bpy.context.scene.objects
                  if ob.type == "LIGHT" and ob.data.type == 'POINT']
        cls.config["light_pos"] = [light.location[j]
                                   for j in range(3) for light in lights]
        cls.config["light_color"] = [
            (light.data.energy * light.data.color / 500.0)[j]
            for j in range(3) for light in lights]

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
        # viewport_info = gpu.state.viewport_get()
        # WIDTH, HEIGHT = viewport_info[2], viewport_info[3]
        offscreen = gpu.types.GPUOffScreen(WIDTH, HEIGHT)

        screen = bpy.context.window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region3d = area.spaces[0].region_3d
                        w_matrix = region3d.window_matrix.copy()
                        v_matrix = region3d.view_matrix
        if w_matrix[1][1] / w_matrix[0][0] < WIDTH / HEIGHT:
            w_matrix[1][1] = w_matrix[0][0] * WIDTH / HEIGHT
        else:
            w_matrix[0][0] = w_matrix[1][1] * HEIGHT / WIDTH
        inv_pers = (w_matrix @ v_matrix).inverted().transposed()

        with offscreen.bind():
            fb = gpu.state.active_framebuffer_get()
            fb.clear(color=(0.2, 0.2, 0.2, 1.0))

            # version = bgl.glGetString(bgl.GL_VERSION)
            # print(version)
            with gpu.matrix.push_pop():
                # reset matrices -> use normalized device coordinates [-1, 1]
                # gpu.matrix.load_matrix(mathutils.Matrix.Identity(4))

                vertices = ((0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT))

                indices = ((0, 1, 2), (2, 1, 3))

                shader = gpu.types.GPUShader(
                    shader_base.v_, shader_base.f_1 +
                                    cls.glsl_nodes.glsl_func_text + shader_base.f_2 +
                                    cls.glsl_nodes.glsl_sdf_text + shader_base.f_3)
                shader.bind()
                # cls.update_config()
                shader.uniform_float("ViewInv", cls.config["inv_view_matrix"])
                #
                shader.uniform_float(
                    "LightPos", cls.config["light_pos"])
                shader.uniform_float(
                    "LightColor", cls.config["light_color"])
                shader.uniform_float("PersInv", inv_pers)
                shader.uniform_float("Size", (WIDTH, HEIGHT))
                shader.uniform_float("CamLoc", cls.config["cam"])
                # shader.uniform_float("LightLoc", cls.config["light"])
                shader.uniform_bool(
                    "IsPers", (cls.config["is_perspective"],))

                batch = batch_for_shader(shader,
                                         'TRIS', {"pos": vertices},
                                         indices=indices)

                projection_matrix = mathutils.Matrix.Diagonal(
                    (2.0 / WIDTH, 2.0 / HEIGHT, 1))
                projection_matrix = mathutils.Matrix.Translation(
                    (-1.0, -1.0, 0.0)) @ projection_matrix.to_4x4()
                gpu.matrix.load_projection_matrix(projection_matrix)

                batch.draw(shader)

            buffer = fb.read_color(0, 0, WIDTH, HEIGHT, 4, 0, 'FLOAT')

        offscreen.free()

        if IMAGE_NAME not in bpy.data.images:
            bpy.data.images.new(IMAGE_NAME, WIDTH, HEIGHT)
        image = bpy.data.images[IMAGE_NAME]
        image.scale(WIDTH, HEIGHT)
        buffer.dimensions = WIDTH * HEIGHT * 4
        image.pixels.foreach_set(buffer)

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

        glsl_nodes = cls.glsl_nodes
        glsl_materials = [mat_node.gen_glsl_material() for mat_node in glsl_nodes.material_node_list]



        cls.frag_shader_code = shader_base.gen_fragment_shader_code(
            glsl_nodes.glsl_func_text,
            glsl_nodes.glsl_sdf_text,
            glsl_materials
        )
        cls.shader = gpu.types.GPUShader(shader_base.v_, cls.frag_shader_code)

        def draw():
            gpu.state.blend_set("ALPHA")
            cls.shader.bind()
            cls.update_config()
            [width, height] = cls.config["size"]
            cls.shader.uniform_float("ViewInv", cls.config["inv_view_matrix"])
            cls.shader.uniform_float("PersInv", cls.config["inv_pers_matrix"])
            cls.shader.uniform_float("Size", (width, height))
            cls.shader.uniform_float("CamLoc", cls.config["cam"])
            cls.shader.uniform_float(
                "LightPos", cls.config["light_pos"])
            cls.shader.uniform_float(
                "LightColor", cls.config["light_color"])
            # cls.shader.uniform_float("LightLoc", cls.config["light"])
            cls.shader.uniform_bool(
                "IsPers", (cls.config["is_perspective"],))
            vertices = ((0, 0), (width, 0), (0, height), (width, height))
            batch = batch_for_shader(cls.shader,
                                     'TRIS', {"pos": vertices},
                                     indices=cls.indices)
            batch.draw(cls.shader)

        return draw

    @classmethod
    def refreshViewport(cls, enabled_show: bool, update_node=False):
        """
        If enabled_show is True, add draw handler to the 3D view. Otherwise, remove draw handler.
        :param enabled_show: bool
        :param update_node: bpy.types.Node
        :return: None
        """
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
