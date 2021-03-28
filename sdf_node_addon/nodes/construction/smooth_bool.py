import bpy
from ...base_types.base_node import CustomNode
from ...redrawViewport import Draw


class SmoothBoolNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'SmoothBool'
    bl_label = 'Smooth Bool'
    bl_icon = 'MOD_BOOLEAN'

    operationItems = [
        ("S_UNION", "Smooth Union", "Smooth Union", "", 0),
        ("S_INTERSECT", "Smooth Intersect", "Smooth Intersect", "", 1),
        ("S_SUBTRACT", "Smooth Subtract", "Smooth Subtract", "", 2)
    ]

    operationLabels = {
        "S_UNION": "Smooth Union",
        "S_INTERSECT": "Smooth Intersect",
        "S_SUBTRACT": "Smooth Subtract"
    }

    def update_prop(self, context):
        Draw.update_callback()

    operation = bpy.props.EnumProperty(name="Operation",
                                       default="S_UNION",
                                       items=operationItems,
                                       update=update_prop)

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="")

    def draw_label(self):
        return self.operationLabels[self.operation]

    def init(self, context):

        self.inputs.new('SdfNodeSocketPositiveFloat', "Smoothness")
        self.inputs[0].default_value = 0.25

        self.inputs.new('NodeSocketFloat', "SDF 1")
        self.inputs[1].hide_value = True

        self.inputs.new('NodeSocketFloat', "SDF 2")
        self.inputs[2].hide_value = True

        self.outputs.new('NodeSocketFloat', "SDF")

        self.width = 147

    def gen_glsl_func(self):
        k = self.inputs[0].default_value

        if self.operation == "S_UNION":
            return f'''float f_{self.index}(float d1, float d2){{
                    float h = max({k}-abs(d1-d2),0.0);
                    return min(d1,d2) - h*h*0.25/{k};
                }}
                '''
        elif self.operation == "S_INTERSECT":
            return f'''float f_{self.index}(float d1, float d2){{
                    float h = max({k}-abs(d1-d2),0.0);
                    return max(d1,d2) + h*h*0.25/{k};
                }}
                '''
        else:
            return f'''float f_{self.index}(float d1, float d2){{
                    float h = max({k}-abs(-d1-d2),0.0);
                    return max(d1,-d2) + h*h*0.25/{k};
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
            input_1_d = '2.0 * MAX_DIST'
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
            input_2_d = '2.0 * MAX_DIST'

        glsl_d = f'''
        float d_{me}_{ref_i}=f_{me}({input_1_d},{input_2_d});
        '''
        return glsl_p, glsl_d
