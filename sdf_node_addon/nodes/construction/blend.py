import bpy
from ...base_types.base_node import CustomNode


class BlendNode(bpy.types.Node, CustomNode):
    '''A Blend node'''

    bl_idname = 'Blend'
    bl_label = 'Blend'
    bl_icon = 'MOD_CAST'

    def init(self, context):

        self.inputs.new('SdfNodeSocketFloat', "Fac")
        self.inputs[0].default_value = 0.5

        self.inputs.new('SdfNodeSocketSdf', "SDF 1")
        self.inputs[1].hide_value = True

        self.inputs.new('SdfNodeSocketSdf', "SDF 2")
        self.inputs[2].hide_value = True

        self.outputs.new('SdfNodeSocketSdf', "SDF")

    def gen_glsl_func(self):
        k = self.inputs[0].default_value

        # (2/(max(k,-1.0)+1)-1, max(k,-1.0))
        # (sqrt(max(1.0-k*k,0.0)), k)
        return f'''
SDFInfo f_{self.index}(SDFInfo d1, SDFInfo d2){{
    float mix = (1-({k})) * d1.sd + ({k}) * d2.sd;
    return (d1.sd > d2.sd) ? SDFInfo(mix, d1.materialID) : SDFInfo(mix, d2.materialID);
}}
'''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num

        if self.inputs[1].links:
            input_1 = self.inputs[1].links[0].from_node
            input_1_p = input_1.index
            input_1_ref = ref_stacks[input_1_p].pop()
            input_1_d = f'd_{input_1_p}_{input_1_ref}'
            glsl_p = f'''
    vec3 p_{input_1_p}_{input_1_ref}=p_{me}_{ref_i};
'''
        else:
            input_1_d = 'SDFInfo(2.0 * MAX_DIST, 0)'
            glsl_p = ''

        if self.inputs[2].links:
            input_2 = self.inputs[2].links[0].from_node
            input_2_p = input_2.index
            input_2_ref = ref_stacks[input_2_p].pop()
            input_2_d = f'd_{input_2_p}_{input_2_ref}'
            glsl_p += f'''
    vec3 p_{input_2_p}_{input_2_ref}=p_{me}_{ref_i};
'''
        else:
            input_2_d = 'SDFInfo(2.0 * MAX_DIST, 0)'

        glsl_d = f'''
    SDFInfo d_{me}_{ref_i}=f_{me}({input_1_d},{input_2_d});
'''
        return glsl_p, glsl_d

    # def gen_glsl_func_simple(self):
    #     k = self.inputs[0].default_value

    #     # (2/(max(k,-1.0)+1)-1, max(k,-1.0))
    #     # (sqrt(max(1.0-k*k,0.0)), k)
    #     return f'''float f_{self.index}(float d1, float d2){{
    #             return (1-({k})) * d1 + ({k}) * d2;
    #         }}
    #         '''

    # def gen_glsl_simple(self, ref_stacks):
    #     me = self.index
    #     ref_i = self.ref_num

    #     if self.inputs[1].links:
    #         input_1 = self.inputs[1].links[0].from_node
    #         input_1_p = input_1.index
    #         input_1_ref = ref_stacks[input_1_p].pop()
    #         input_1_d = f'd_{input_1_p}_{input_1_ref}'
    #         glsl_p = f'''
    #         vec3 p_{input_1_p}_{input_1_ref}=p_{me}_{ref_i};
    #         '''
    #     else:
    #         input_1_d = '2.0 * MAX_DIST'
    #         glsl_p = ''

    #     if self.inputs[2].links:
    #         input_2 = self.inputs[2].links[0].from_node
    #         input_2_p = input_2.index
    #         input_2_ref = ref_stacks[input_2_p].pop()
    #         input_2_d = f'd_{input_2_p}_{input_2_ref}'
    #         glsl_p += f'''
    #         vec3 p_{input_2_p}_{input_2_ref}=p_{me}_{ref_i};
    #         '''
    #     else:
    #         input_2_d = '2.0 * MAX_DIST'

    #     glsl_d = f'''
    #     float d_{me}_{ref_i}=f_{me}({input_1_d},{input_2_d});
    #     '''
    #     return glsl_p, glsl_d
