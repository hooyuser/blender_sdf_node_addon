import bpy
from ...base_types.base_node import CustomNode
from ...redrawViewport import Draw


class BoolNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'Bool'
    bl_label = 'Bool'
    bl_icon = 'MOD_BOOLEAN'

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

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self, node_info):
        if self.inputs[0].links:
            input_0_p = self.inputs[0].links[0].from_node.index
            input_0_d = 'd_' + str(input_0_p)
            glsl_p_code = '''
            vec3 p_%d=p_%d;
            ''' % (input_0_p, self.index)
        else:
            input_0_d = '2.0 * MAX_DIST'
            glsl_p_code = ''

        if self.inputs[1].links:
            input_1_p = self.inputs[1].links[0].from_node.index
            input_1_d = 'd_' + str(input_1_p)
            glsl_p_code += '''
            vec3 p_%d=p_%d;
            ''' % (input_1_p, self.index)
        else:
            input_1_d = '2.0 * MAX_DIST'

        node_info.glsl_p_list.append(glsl_p_code)

        if self.operation == "UNION":
            glsl_d_code = '''
            float d_{}=min({},{});
            '''.format(self.index, input_0_d, input_1_d)
        elif self.operation == "INTERSECT":
            glsl_d_code = '''
            float d_{}=max({},{});
            '''.format(self.index, input_0_d, input_1_d)
        else:
            glsl_d_code = '''
            float d_{}=max({},-{});
            '''.format(self.index, input_0_d, input_1_d)

        node_info.glsl_d_list.append(glsl_d_code)
