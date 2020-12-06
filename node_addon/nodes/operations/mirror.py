import bpy
from ...base_types.base_node import CustomNode
from ...redrawViewport import Draw


class MirrorNode(bpy.types.Node, CustomNode):
    '''Mirror node'''

    bl_idname = 'Mirror'
    bl_label = 'Mirror'
    bl_icon = 'MOD_MIRROR'

    def update_prop(self, context):
        Draw.update_callback()

    mirror_axis = bpy.props.BoolVectorProperty(update=update_prop)

    def draw_buttons(self, context, layout):
        col = layout.column()
        row = col.row()
        row.label(text="Axis")
        subrow = row.row(align=True)
        subrow.prop(self, "mirror_axis", index=0, text="X", toggle=True)
        subrow.prop(self, "mirror_axis", index=1, text="Y", toggle=True)
        subrow.prop(self, "mirror_axis", index=2, text="Z", toggle=True)

    def init(self, context):
        self.inputs.new('SdfNodeSocketOperation', "Distance")

        self.outputs.new('SdfNodeSocketOperation', "Operation")

    def gen_glsl(self):

        if self.mirror_axis[0]:
            glsl_code = '''
            float d;
            '''

        return glsl_code
