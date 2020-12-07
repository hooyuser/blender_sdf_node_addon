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
        self.inputs.new('NodeSocketFloat', "Distance")
        self.inputs[0].hide_value = True

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        if self.inputs[0].links:
            last = self.inputs[0].links[0].from_node.index
            me = self.index
            x = 'abs' if self.mirror_axis[0] else ''
            y = 'abs' if self.mirror_axis[1] else ''
            z = 'abs' if self.mirror_axis[2] else ''
            return f'''
                vec3 p_{last} = vec3({x}(p_{me}.x),{y}(p_{me}.y),{z}(p_{me}.z));
            ''', f'''
                float d_{me} = d_{last};
            '''
        else:
            return '', f'''
                float d_{me} = 2 * MAX_DIST;
            '''
