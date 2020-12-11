import bpy

from ...base_types.base_node import CustomNode


class FbmNoiseNode(bpy.types.Node, CustomNode):
    '''Simplex Noise node'''

    bl_idname = 'FbmNoise'
    bl_label = 'FBM Noise'
    bl_icon = 'MOD_BEVEL'

    def init(self, context):
        self.inputs.new('SdfNodeSocketFloat', "Amplitude")
        self.inputs[0].default_value = 0.5

        self.inputs.new('SdfNodeSocketFloat', "Frequency")
        self.inputs[1].default_value = 2.0

        self.inputs.new('SdfNodeSocketFloat', "Phase Shift")
        self.inputs[2].default_value = 0.0

        self.inputs.new('SdfNodeSocketFloat', "Amplitude Decay")
        self.inputs[3].default_value = 0.5

        self.inputs.new('SdfNodeSocketPositiveInt', "Iteration")
        self.inputs[4].default_value = 1

        self.inputs.new('SdfNodeSocketFloat', "X Offset")
        self.inputs.new('SdfNodeSocketFloat', "Y Offset")
        self.inputs.new('SdfNodeSocketFloat', "Z Offset")

        self.inputs.new('NodeSocketFloat', "SDF")
        self.inputs[8].hide_value = True

        self.outputs.new('NodeSocketFloat', "SDF")

        self.width = 174

    def gen_glsl_func(self):
        if self.inputs[8].links:
            amplitude = self.inputs[0].default_value
            frequency = self.inputs[1].default_value
            shift = self.inputs[2].default_value
            decay = self.inputs[3].default_value
            num = self.inputs[4].default_value
            x = self.inputs[5].default_value
            y = self.inputs[6].default_value
            z = self.inputs[7].default_value

            return f'''
                float f_{self.index}(float d, vec3 p)
                {{
                    vec3 x = p + vec3({x},{y},{z});
                    float amplitude = {amplitude};
                    vec3 shift = vec3({shift});
                    float y = 0.0;
                    for(int i=0; i<{num}; i++)
                    {{
                        y += amplitude * valueNoise(x);
                        amplitude *= {decay};
                        x = {frequency} * m3 * x + shift;
                    }}
                    return d + y;
                }}
                '''
        else:
            return ''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num
        if self.inputs[8].links:
            last_node = self.inputs[8].links[0].from_node
            last = last_node.index
            last_ref = ref_stacks[last].pop()

            glsl_p = f'''
                vec3 p_{last}_{last_ref} = p_{me}_{ref_i};
            '''
            glsl_d = f'''
                float d_{me}_{ref_i}=f_{me}(d_{last}_{last_ref}, p);
            '''
        else:
            glsl_p = ''
            glsl_d = f'''
                float d_{me}_{ref_i} = 2 * MAX_DIST;
            '''

        return glsl_p, glsl_d
