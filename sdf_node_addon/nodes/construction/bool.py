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
        self.inputs.new('NodeSocketFloat', "SDF 1")
        self.inputs[0].hide_value = True

        self.inputs.new('NodeSocketFloat', "SDF 2")
        self.inputs[1].hide_value = True

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):

        if self.operation == "UNION":
            return f'''float f_{self.index}(float d1, float d2){{
                    return min(d1,d2);
                }}
                '''
        elif self.operation == "INTERSECT":
            return f'''float f_{self.index}(float d1, float d2){{
                    return max(d1,d2);
                }}
                '''
        else:
            return f'''float f_{self.index}(float d1, float d2){{
                    return max(d1,-d2);
                }}
                '''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num

        if self.inputs[0].links:
            input_0 = self.inputs[0].links[0].from_node
            input_0_p = input_0.index
            input_0_ref = ref_stacks[input_0_p].pop()
            input_0_d = f'd_{input_0_p}_{input_0_ref}'
            glsl_p = f'''
            vec3 p_{input_0_p}_{input_0_ref}=p_{me}_{ref_i};
            '''
        else:
            input_0_d = '2.0 * MAX_DIST'
            glsl_p = ''

        if self.inputs[1].links:
            input_1 = self.inputs[1].links[0].from_node
            input_1_p = input_1.index
            input_1_ref = ref_stacks[input_1_p].pop()
            input_1_d = f'd_{input_1_p}_{input_1_ref}'
            glsl_p += f'''
            vec3 p_{input_1_p}_{input_1_ref}=p_{me}_{ref_i};
            '''
        else:
            input_1_d = '2.0 * MAX_DIST'

        glsl_d = f'''
        float d_{me}_{ref_i}=f_{me}({input_0_d},{input_1_d});
        '''
        return glsl_p, glsl_d
