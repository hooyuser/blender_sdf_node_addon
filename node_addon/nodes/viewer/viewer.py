import bpy
from ...base_types.base_node import CustomNode
from ...redrawViewport import Draw


# def main():
#     IMAGE_NAME = "Generated Image"
#     WIDTH = 1920
#     HEIGHT = 1080
#     RING_AMOUNT = 10

#     offscreen = gpu.types.GPUOffScreen(WIDTH, HEIGHT)

#     with offscreen.bind():
#         bgl.glClearColor(0.0, 0.0, 0.0, 0.0)
#         bgl.glClear(bgl.GL_COLOR_BUFFER_BIT)
#         with gpu.matrix.push_pop():
#             # reset matrices -> use normalized device coordinates [-1, 1]
#             gpu.matrix.load_matrix(Matrix.Identity(4))
#             gpu.matrix.load_projection_matrix(Matrix.Identity(4))

#             for i in range(RING_AMOUNT):
#                 draw_circle_2d((random.uniform(-1, 1), random.uniform(-1, 1)),
#                                (1, 1, 1, 1), random.uniform(0.1, 1), 20)

#         buffer = bgl.Buffer(bgl.GL_BYTE, WIDTH * HEIGHT * 4)
#         bgl.glReadBuffer(bgl.GL_BACK)
#         bgl.glReadPixels(0, 0, WIDTH, HEIGHT, bgl.GL_RGBA,
#                          bgl.GL_UNSIGNED_BYTE, buffer)

#     offscreen.free()

#     if not IMAGE_NAME in bpy.data.images:
#         bpy.data.images.new(IMAGE_NAME, WIDTH, HEIGHT)
#     image = bpy.data.images[IMAGE_NAME]
#     image.scale(WIDTH, HEIGHT)
#     image.pixels = [v / 255 for v in buffer]


class HelloWorldOperator(bpy.types.Operator):
    bl_idname = "wm.hello_world"
    bl_label = "Minimal Operator"

    def execute(self, context):
        Draw.render(context)
        print("Hello World")
        return {'FINISHED'}


class ViewerNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'Viewer'
    bl_label = 'Viewer'
    bl_icon = 'RESTRICT_RENDER_OFF'

    def redraw3DViewport(self, context):
        Draw.refreshViewport(self.enabled)

    enabled = bpy.props.BoolProperty(name="Enabled",
                                     default=False,
                                     update=redraw3DViewport)

    def update(self):  # rewrite update function
        if not self.inputs[0].links:
            Draw.refreshViewport(False)

    def draw_buttons(self, context, layout):
        layout.prop(self, "enabled", text="Show SDF")
        layout.operator("wm.hello_world", text='Render')

    # def update(self):
    #     if self.inputs[0].links:
    #         Draw.refreshViewport(False)
    #         Draw.refreshViewport(True)

    def init(self, context):
        self.inputs.new('NodeSocketFloat', "SDF")
        self.inputs[0].hide_value = True

    def free(self):
        Draw.refreshViewport(False)
