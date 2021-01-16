import bpy
import math

from ...base_types.base_node import CustomNode

float_category = ['SdfNodeSocketFloat', 'SdfNodeSocketPositiveFloat']


class FloatMathNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'FloatMath'
    bl_label = 'Float Math'
    bl_icon = 'FORCE_HARMONIC'

    operationItems = [
        ("ADD", "Add", "Add"),
        ('SUBTRACT', 'Subtract', 'Subtract'),
        ("MULTIPLY", "Multiply", "Multiply"),
        ("DIVIDE", "Divide", "Divide"),
        ("ABS", "Abs", "Absolute Value"),
        ("MAX", "Max", "Maximum"),
        ("MIN", "Min", "Minimum"),
        ("SIN", "Sin", "Sine"),
        ('COS', 'Cos', 'Cosine'),
        ('TAN', 'Tan', 'Tangent'),
    ]

    operationLabels = {
        "ADD": "Add",
        'SUBTRACT': 'Subtract',
        'MULTIPLY': "Multiply",
        'DIVIDE': "Divide",
        "MAX": "Max",
        "MIN": "Min",
        "ABS": "Abs",
        "SIN": "Sin",
        "COS": "Cos",
        "TAN": "Tan",
    }

    operationFunctions = {
        'ADD': lambda x, y: x + y,
        'SUBTRACT': lambda x, y: x - y,
        'MULTIPLY': lambda x, y: x * y,
        'DIVIDE': lambda x, y: x / y,
        "MAX": lambda x, y: max(x, y),
        "MIN": lambda x, y: min(x, y),
        "ABS": lambda x, y: abs(x),
        'SIN': lambda x, y: math.sin(x),
        'COS': lambda x, y: math.cos(x),
        'TAN': lambda x, y: math.tan(x),
    }

    func_dict = {
        **dict.fromkeys([
            'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', "MAX", "MIN"
        ], 2),
        **dict.fromkeys(["ABS", 'SIN', 'COS', 'TAN'], 1)
    }

    def evaluate(self, operation):
        self.value = self.operationFunctions[operation](
            self.inputs[0].default_value, self.inputs[1].default_value)

    def update_operation(self, context):
        if self.func_dict[self.operation] == 1:
            self.inputs[0].name = 'X'
            self.inputs[1].hide = True
        else:
            self.inputs[0].name = 'X1'
            self.inputs[1].hide = False
        self.evaluate(self.operation)

    def update_value(self, context):
        for link in self.outputs[0].links:
            link.to_socket.default_value = self.value

    operation: bpy.props.EnumProperty(name="Operation",
                                      default="ADD",
                                      items=operationItems,
                                      update=update_operation)

    value: bpy.props.FloatProperty(update=update_value)

    def init(self, context):
        self.index = -2
        self.inputs.new('SdfNodeSocketFloat', "X1")
        self.inputs.new('SdfNodeSocketFloat', "X2")

        self.outputs.new('SdfNodeSocketFloat', "Y")

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="")

    def draw_label(self):
        return self.operationLabels[self.operation]

    def update(self):
        if self.outputs and self.outputs[0].links:
            tree = bpy.context.space_data.edit_tree
            self.evaluate(self.operation)
            for link in self.outputs[0].links:
                if link.to_socket.bl_idname in float_category:
                    link.to_socket.default_value = self.value
                else:
                    tree.links.remove(link)
