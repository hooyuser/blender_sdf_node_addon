import bpy
from ...base_types.base_node import CustomNode
from ...redrawViewport import Draw


class BoolNode(CustomNode):
    '''A simple input node'''

    bl_idname = 'Bool'
    bl_label = 'Bool'
    bl_icon = 'PLUS'

    operationItems = [
        ("UNION", "Union", "Union", "", 0),
        ("INTERSECT", "Intersect", "Intersect", "", 1),
        ("SUBTRACT", "Subtract", "Subtract", "", 2),
    ]

    operationLabels = {
        "UNION": "Union",
        "INTERSECT": "Intersect",
        "SUBTRACT": "Subtract"
    }

    def update_prop(self, context):
        Draw.update_callback()

    operation = bpy.props.EnumProperty(name="Operation",
                                       default="UNION",
                                       items=operationItems,
                                       update=update_prop)

    def draw_buttons(self, context, layout):

        layout.prop(self, "operation", text="")

    def draw_label(self):
        return self.operationLabels[self.operation]

    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Distance 1")
        self.inputs[0].hide_value = True

        self.inputs.new('NodeSocketFloat', "Distance 2")
        self.inputs[1].hide_value = True

        self.outputs.new('SdfNodeSocketFloat', "Distance")

    def gen_glsl(self):
        input_0 = 'd_' + str(bpy.data.node_groups["NodeTree"].nodes[
            self.inputs[0].links[0].from_node.name].index
                             ) if self.inputs[0].links else '2.0 * MAX_DIST'
        input_1 = 'd_' + str(bpy.data.node_groups["NodeTree"].nodes[
            self.inputs[1].links[0].from_node.name].index
                             ) if self.inputs[1].links else '2.0 * MAX_DIST'

        if self.operation == "UNION":
            glsl_code = '''
            float d_{}=min({},{});
            '''.format(self.index, input_0, input_1)
        elif self.operation == "INTERSECT":
            glsl_code = '''
            float d_{}=max({},{});
            '''.format(self.index, input_0, input_1)
        else:
            glsl_code = '''
            float d_{}=max(-{},{});
            '''.format(self.index, input_0, input_1)

        return glsl_code
