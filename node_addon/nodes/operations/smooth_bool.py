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

        self.inputs.new('NodeSocketFloat', "Distance 1")
        self.inputs[1].hide_value = True

        self.inputs.new('NodeSocketFloat', "Distance 2")
        self.inputs[2].hide_value = True

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        k = self.inputs[0].default_value
        me = self.index

        if self.inputs[1].links:
            input_1_p = self.inputs[1].links[0].from_node.index
            input_1_d = 'd_' + str(input_1_p)
            glsl_p = f'''
            vec3 p_{input_1_p}=p_{me};
            '''
        else:
            input_1_d = '2.0 * MAX_DIST'
            glsl_p = ''

        if self.inputs[2].links:
            input_2_p = self.inputs[2].links[0].from_node.index
            input_2_d = 'd_' + str(input_2_p)
            glsl_p += f'''
            vec3 p_{input_2_p}=p_{me};
            '''
        else:
            input_2_d = '2.0 * MAX_DIST'

        if self.operation == "S_UNION":
            glsl_d = f'''
            float h_{me} = max({k}-abs({input_1_d}-{input_2_d}),0.0);
            float d_{me} = min({input_1_d},{input_2_d}) - h_{me}*h_{me}*0.25/{k};
            '''
        elif self.operation == "S_INTERSECT":
            glsl_d = f'''
            float h_{me} = max({k}-abs({input_1_d}-{input_2_d}),0.0);
            float d_{me} = max({input_1_d},{input_2_d}) + h_{me}*h_{me}*0.25/{k};
            '''
        else:
            glsl_d = f'''
            float h_{me} = max({k}-abs(-{input_1_d}-{input_2_d}),0.0);
            float d_{me} = max({input_1_d},-{input_2_d}) + h_{me}*h_{me}*0.25/{k};
            '''

        return glsl_p, glsl_d
