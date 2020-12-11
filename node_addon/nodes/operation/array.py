import bpy
from ...base_types.base_node import CustomNode


class ArrayNode(bpy.types.Node, CustomNode):
    '''Array node'''

    bl_idname = 'Array'
    bl_label = 'Array'
    bl_icon = 'MOD_ARRAY'

    def init(self, context):
        self.inputs.new('SdfNodeSocketPositiveFloat', "Spacing")
        self.inputs[0].default_value = 1

        self.inputs.new('SdfNodeSocketPositiveInt', "x num")
        self.inputs[1].default_value = 1

        self.inputs.new('SdfNodeSocketPositiveInt', "y num")
        self.inputs[2].default_value = 1

        self.inputs.new('SdfNodeSocketPositiveInt', "z num")
        self.inputs[3].default_value = 1

        self.inputs.new('NodeSocketFloat', "SDF")
        self.inputs[4].hide_value = True

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):
        if self.inputs[4].links:
            s = self.inputs[0].default_value
            x = float(self.inputs[1].default_value - 1)
            y = float(self.inputs[2].default_value - 1)
            z = float(self.inputs[3].default_value - 1)

            return f'''vec3 g_{self.index}(vec3 p){{
                    return p-({s})*clamp(round(p/{s}),vec3(0.0),vec3({x},{y},{z}));
                }}
                '''
        else:
            return ''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num
        if self.inputs[4].links:
            last_node = self.inputs[4].links[0].from_node
            last = last_node.index
            last_ref = ref_stacks[last].pop()

            glsl_p = f'''
                vec3 p_{last}_{last_ref} = g_{me}(p_{me}_{ref_i});
            '''
            glsl_d = f'''
                float d_{me}_{ref_i}=d_{last}_{last_ref};
            '''
        else:
            glsl_p = ''
            glsl_d = f'''
                float d_{me}_{ref_i} = 2 * MAX_DIST;
            '''

        return glsl_p, glsl_d
