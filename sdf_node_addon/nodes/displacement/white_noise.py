import bpy

from ...base_types.base_node import CustomNode


class WhiteNoiseNode(bpy.types.Node, CustomNode):
    '''WhiteNoise node'''

    bl_idname = 'WhiteNoise'
    bl_label = 'White Noise'
    bl_icon = 'MOD_BEVEL'

    def init(self, context):
        self.inputs.new('SdfNodeSocketFloat', "Time")
        self.inputs.new('SdfNodeSocketFloat', "Magnitude")
        self.inputs[1].default_value = 1
        self.inputs.new('SdfNodeSocketFloat', "X Offset")
        self.inputs.new('SdfNodeSocketFloat', "Y Offset")
        self.inputs.new('SdfNodeSocketFloat', "Z Offset")

        self.inputs.new('SdfNodeSocketSdf', "SDF")
        self.inputs[5].hide_value = True

        self.outputs.new('SdfNodeSocketSdf', "SDF")

    def gen_glsl_func(self):
        if self.inputs[5].links:
            t = self.inputs[0].default_value
            k = self.inputs[1].default_value
            x = self.inputs[2].default_value
            y = self.inputs[3].default_value
            z = self.inputs[4].default_value

            return f'''
                SDFInfo f_{self.index}(SDFInfo d, vec3 p){{
                    return SDFInfo(d.sd + ({k}) * random(vec4(p+vec3({x},{y},{z}),{t})), d.materialID);
                }}
                '''
        else:
            return ''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num
        if self.inputs[5].links:
            last_node = self.inputs[5].links[0].from_node
            last = last_node.index
            last_ref = ref_stacks[last].pop()

            glsl_p = f'''
                vec3 p_{last}_{last_ref} = p_{me}_{ref_i};
            '''
            glsl_d = f'''
                SDFInfo d_{me}_{ref_i}=f_{me}(d_{last}_{last_ref}, p);
            '''
        else:
            glsl_p = ''
            glsl_d = f'''
                SDFInfo d_{me}_{ref_i} = SDFInfo(2.0 * MAX_DIST, 0);
            '''

        return glsl_p, glsl_d

    # def gen_glsl_func_simple(self):
    #     if self.inputs[5].links:
    #         t = self.inputs[0].default_value
    #         k = self.inputs[1].default_value
    #         x = self.inputs[2].default_value
    #         y = self.inputs[3].default_value
    #         z = self.inputs[4].default_value

    #         return f'''
    #             float f_{self.index}(float d, vec3 p){{
    #                 return d + ({k}) * random(vec4(p+vec3({x},{y},{z}),{t}));
    #             }}
    #             '''
    #     else:
    #         return ''

    # def gen_glsl_simple(self, ref_stacks):
    #     me = self.index
    #     ref_i = self.ref_num
    #     if self.inputs[5].links:
    #         last_node = self.inputs[5].links[0].from_node
    #         last = last_node.index
    #         last_ref = ref_stacks[last].pop()

    #         glsl_p = f'''
    #             vec3 p_{last}_{last_ref} = p_{me}_{ref_i};
    #         '''
    #         glsl_d = f'''
    #             float d_{me}_{ref_i}=f_{me}(d_{last}_{last_ref}, p);
    #         '''
    #     else:
    #         glsl_p = ''
    #         glsl_d = f'''
    #             float d_{me}_{ref_i} = 2.0 * MAX_DIST;
    #         '''

    #     return glsl_p, glsl_d
