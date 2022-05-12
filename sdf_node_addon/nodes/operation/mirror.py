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

    mirror_axis: bpy.props.BoolVectorProperty(update=update_prop)

    def draw_buttons(self, context, layout):
        col = layout.column()
        row = col.row()
        row.label(text="Plane")
        subrow = row.row(align=True)
        subrow.prop(self, "mirror_axis", index=0, text="X", toggle=True)
        subrow.prop(self, "mirror_axis", index=1, text="Y", toggle=True)
        subrow.prop(self, "mirror_axis", index=2, text="Z", toggle=True)

    def init(self, context):
        self.inputs.new('SdfNodeSocketSdf', "SDF")
        self.inputs[0].hide_value = True

        self.outputs.new('SdfNodeSocketSdf', "SDF")

    def gen_glsl_func(self):
        if self.inputs[0].links:
            x = '-' if self.mirror_axis[0] else ''
            y = '-' if self.mirror_axis[1] else ''
            z = '-' if self.mirror_axis[2] else ''
            return f'''vec3 g_{self.index}(vec3 p){{
                    return vec3({x}(p.x),{y}(p.y),{z}(p.z));
                }}
                '''
        else:
            return ''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num
        if self.inputs[0].links:
            last_node = self.inputs[0].links[0].from_node
            last = last_node.index
            last_ref = ref_stacks[last].pop()

            glsl_p = f'''
                vec3 p_{last}_{last_ref} = g_{me}(p_{me}_{ref_i});
            '''
            glsl_d = f'''
                SDFInfo d_{me}_{ref_i}=d_{last}_{last_ref};
            '''
        else:
            glsl_p = ''
            glsl_d = f'''
                SDFInfo d_{me}_{ref_i} = SDFInfo(2.0 * MAX_DIST, 0);
            '''

        return glsl_p, glsl_d

    # def gen_glsl_func_simple(self):
    #     if self.inputs[0].links:
    #         x = '-' if self.mirror_axis[0] else ''
    #         y = '-' if self.mirror_axis[1] else ''
    #         z = '-' if self.mirror_axis[2] else ''
    #         return f'''vec3 g_{self.index}(vec3 p){{
    #                 return vec3({x}(p.x),{y}(p.y),{z}(p.z));
    #             }}
    #             '''
    #     else:
    #         return ''

    # def gen_glsl_simple(self, ref_stacks):
    #     me = self.index
    #     ref_i = self.ref_num
    #     if self.inputs[0].links:
    #         last_node = self.inputs[0].links[0].from_node
    #         last = last_node.index
    #         last_ref = ref_stacks[last].pop()

    #         glsl_p = f'''
    #             vec3 p_{last}_{last_ref} = g_{me}(p_{me}_{ref_i});
    #         '''
    #         glsl_d = f'''
    #             float d_{me}_{ref_i}=d_{last}_{last_ref};
    #         '''
    #     else:
    #         glsl_p = ''
    #         glsl_d = f'''
    #             float d_{me}_{ref_i} = 2.0 * MAX_DIST;
    #         '''

    #     return glsl_p, glsl_d
