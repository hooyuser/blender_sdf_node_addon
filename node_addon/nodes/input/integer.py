import bpy

from ...base_types.base_node import CustomNode

int_category = [
    'SdfNodeSocketPositiveInt', 'SdfNodeSocketFloat',
    'SdfNodeSocketPositiveFloat'
]


class IntegerInputNode(bpy.types.Node, CustomNode):
    '''An integer input node'''

    bl_idname = 'IntegerInput'
    bl_label = 'Integer'
    bl_icon = 'ITALIC'

    def update_prop(self, context):
        for link in self.outputs[0].links:
            link.to_socket.default_value = self.value
            # Draw.update_callback(update_node=link.to_node)

    value = bpy.props.IntProperty(update=update_prop)

    def init(self, context):
        self.index = -3
        self.outputs.new('SdfNodeSocketPositiveInt', "Value")

    def draw_buttons(self, context, layout):
        # create a slider for int values
        layout.prop(self, 'value', text='Integer')

    def update(self):
        if self.outputs[0].links:
            tree = bpy.context.space_data.edit_tree
            for link in self.outputs[0].links:
                if link.to_socket.bl_idname in int_category:
                    link.to_socket.default_value = self.value
                else:
                    tree.links.remove(link)
