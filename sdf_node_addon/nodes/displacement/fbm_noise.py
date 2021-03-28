import bpy

from ...base_types.base_node import CustomNode
from ...redrawViewport import Draw


class FbmNoiseNode(bpy.types.Node, CustomNode):
    '''Simplex Noise node'''

    bl_idname = 'FbmNoise'
    bl_label = 'FBM Noise'
    bl_icon = 'MOD_BEVEL'

    operationItems = [
        ("SIMPLEX", "Simplex", "Simplex", "", 0),
        ("VALUE", "Value", "Value", "", 1),
    ]

    operationLabels = {
        "UNION": "Simplex",
        "INTERSECT": "Value",
    }

    def update_prop(self, context):
        Draw.update_callback()

    operation = bpy.props.EnumProperty(name="Operation",
                                       default="SIMPLEX",
                                       items=operationItems,
                                       update=update_prop)

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="Type")

    def init(self, context):
        self.inputs.new('SdfNodeSocketFloat', "Amplitude")
        self.inputs["Amplitude"].default_value = 0.5

        self.inputs.new('SdfNodeSocketFloat', "Scale")
        self.inputs["Scale"].default_value = 1.0

        self.inputs.new('SdfNodeSocketFloat', "Frequency")
        self.inputs["Frequency"].default_value = 2.0

        self.inputs.new('SdfNodeSocketFloat', "Phase Shift")
        self.inputs["Phase Shift"].default_value = 0.0

        self.inputs.new('SdfNodeSocketFloat', "Amplitude Decay")
        self.inputs["Amplitude Decay"].default_value = 0.5

        self.inputs.new('SdfNodeSocketPositiveInt', "Iteration")
        self.inputs["Iteration"].default_value = 1

        self.inputs.new('SdfNodeSocketFloat', "X Offset")
        self.inputs.new('SdfNodeSocketFloat', "Y Offset")
        self.inputs.new('SdfNodeSocketFloat', "Z Offset")

        self.inputs.new('NodeSocketFloat', "SDF")
        self.inputs['SDF'].hide_value = True

        self.outputs.new('NodeSocketFloat', "SDF")

        self.width = 174

    def gen_glsl_func(self):
        if self.inputs['SDF'].links:
            amplitude = self.inputs['Amplitude'].default_value
            scale = self.inputs['Scale'].default_value
            frequency = self.inputs["Frequency"].default_value
            shift = self.inputs["Phase Shift"].default_value
            decay = self.inputs["Amplitude Decay"].default_value
            num = self.inputs["Iteration"].default_value
            x = self.inputs["X Offset"].default_value
            y = self.inputs["Y Offset"].default_value
            z = self.inputs["Z Offset"].default_value

            type = 'simplex' if self.operation == 'SIMPLEX' else 'value'

            return f'''
                float f_{self.index}(float d, vec3 p)
                {{
                    vec3 x = p / ({scale}) - vec3({x},{y},{z});
                    float amplitude = {amplitude};
                    vec3 shift = vec3({shift});
                    float y = 0.0;
                    for(int i=0; i<{num}; i++)
                    {{
                        y += amplitude * {type}Noise3D(x);
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
        if self.inputs['SDF'].links:
            last_node = self.inputs['SDF'].links[0].from_node
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
