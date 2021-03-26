import bpy
from ...base_types.base_node import CustomNode
from ...redrawViewport import Draw


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
