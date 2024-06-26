import bpy
from ...base_types.base_node import CustomNode


class TwistNode(bpy.types.Node, CustomNode):
    '''Twist node'''

    bl_idname = 'Twist'
    bl_label = 'Twist'
    bl_icon = 'MOD_SCREW'

    def init(self, context):
        self.inputs.new('SdfNodeSocketFloat', "Intensity")
        self.inputs[0].default_value = 0

        self.inputs.new('SdfNodeSocketSdf', "SDF")
        self.inputs[1].hide_value = True

        self.outputs.new('SdfNodeSocketSdf', "SDF")

    def gen_glsl_func(self):
        if self.inputs[1].links:
            k = self.inputs[0].default_value / 10
            return f'''vec3 g_{self.index}(vec3 p){{
                    float c = cos({k}*p.z);
                    float s = sin({k}*p.z);
                    mat2 m = mat2(c,-s,s,c);
                    return vec3(m*p.xy,p.z);
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
                vec3 p_{last}_{last_ref} = g_{me}(p_{me}_{ref_i});
            '''
            glsl_d = f'''
                SDFInfo d_{me}_{ref_i} = d_{last}_{last_ref};
            '''
        else:
            glsl_p = ''
            glsl_d = f'''
                SDFInfo d_{me}_{ref_i} = SDFInfo(2.0 * MAX_DIST, 0);
            '''

        return glsl_p, glsl_d

    # def gen_glsl_func_simple(self):
    #     if self.inputs[1].links:
    #         k = self.inputs[0].default_value / 10
    #         return f'''vec3 g_{self.index}(vec3 p){{
    #                 float c = cos({k}*p.z);
    #                 float s = sin({k}*p.z);
    #                 mat2 m = mat2(c,-s,s,c);
    #                 return vec3(m*p.xy,p.z);
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
