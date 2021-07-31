import bpy

from ...base_types.base_node import CustomNode


class RoundNode(bpy.types.Node, CustomNode):
    '''Round node'''

    bl_idname = 'Round'
    bl_label = 'Round'
    bl_icon = 'MOD_BEVEL'

    def init(self, context):

        self.inputs.new('SdfNodeSocketPositiveFloat', "Radius")
        self.inputs[0].default_value = 0.1

        self.inputs.new('NodeSocketFloat', "SDF")
        self.inputs[1].hide_value = True

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):
        if self.inputs[1].links:
            return f'''
                SDFInfo f_{self.index}(SDFInfo d){{
                    return SDFInfo(d.sd - ({self.inputs[0].default_value}), d.materialID);
                }}
                '''
        else:
            return ''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num
        if self.inputs[1].links:
            last_node = self.inputs[1].links[0].from_node
            last = last_node.index
            last_ref = ref_stacks[last].pop()

            glsl_p = f'''
                vec3 p_{last}_{last_ref} = p_{me}_{ref_i};
            '''
            glsl_d = f'''
                SDFInfo d_{me}_{ref_i}=f_{me}(d_{last}_{last_ref});
            '''
        else:
            glsl_p = ''
            glsl_d = f'''
                SDFInfo d_{me}_{ref_i} = SDFInfo(2.0 * MAX_DIST, 0);
            '''

        return glsl_p, glsl_d

    # def gen_glsl_func_simple(self):
    #     if self.inputs[1].links:
    #         return f'''
    #             float f_{self.index}(float d){{
    #                 return d - ({self.inputs[0].default_value});
    #             }}
    #             '''
    #     else:
    #         return ''

    # def gen_glsl_simple(self, ref_stacks):
    #     me = self.index
    #     ref_i = self.ref_num
    #     if self.inputs[1].links:
    #         last_node = self.inputs[1].links[0].from_node
    #         last = last_node.index
    #         last_ref = ref_stacks[last].pop()

    #         glsl_p = f'''
    #             vec3 p_{last}_{last_ref} = p_{me}_{ref_i};
    #         '''
    #         glsl_d = f'''
    #             float d_{me}_{ref_i}=f_{me}(d_{last}_{last_ref});
    #         '''
    #     else:
    #         glsl_p = ''
    #         glsl_d = f'''
    #             float d_{me}_{ref_i} = 2.0 * MAX_DIST;
    #         '''

    #     return glsl_p, glsl_d
