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

        self.inputs.new('SdfNodeSocketFloat', "Smoothness")
        self.inputs[0].default_value = 0.25

        self.inputs.new('NodeSocketFloat', "Distance 1")
        self.inputs[1].hide_value = True

        self.inputs.new('NodeSocketFloat', "Distance 2")
        self.inputs[2].hide_value = True

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        k = self.inputs[0].default_value
        input_1 = 'd_' + str(bpy.data.node_groups["NodeTree"].nodes[
            self.inputs[1].links[0].from_node.name].index
                             ) if self.inputs[1].links else '2.0 * MAX_DIST'
        input_2 = 'd_' + str(bpy.data.node_groups["NodeTree"].nodes[
            self.inputs[2].links[0].from_node.name].index
                             ) if self.inputs[2].links else '2.0 * MAX_DIST'

        if self.operation == "S_UNION":
            glsl_code = '''
            float h_{} = max({}-abs({}-{}),0.0);
            float d_{} = min({},{}) - h_{}*h_{}*0.25/{};
            '''.format(self.index, k, input_1, input_2, self.index, input_1,
                       input_2, self.index, self.index, k)
        elif self.operation == "S_INTERSECT":
            glsl_code = '''
            float h_{} = max({}-abs({}-{}),0.0);
            float d_{} = max({},{}) + h_{}*h_{}*0.25/{};
            '''.format(self.index, k, input_1, input_2, self.index, input_1,
                       input_2, self.index, self.index, k)
        else:
            glsl_code = '''
            float h_{} = max({}-abs(-{}-{}),0.0);
            float d_{} = max(-{},{}) + h_{}*h_{}*0.25/{};
            '''.format(self.index, k, input_1, input_2, self.index, input_1,
                       input_2, self.index, self.index, k)

        return glsl_code
