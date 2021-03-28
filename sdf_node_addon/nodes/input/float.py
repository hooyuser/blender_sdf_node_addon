import bpy

from ...base_types.base_node import CustomNode
# from ...redrawViewport import Draw

float_category = ['SdfNodeSocketFloat', 'SdfNodeSocketPositiveFloat']


class FloatInputNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'FloatInput'
    bl_label = 'Float'
    bl_icon = 'FILE_FONT'

    def update_prop(self, context):
        for link in self.outputs[0].links:
            link.to_socket.default_value = self.value
            # Draw.update_callback(update_node=link.to_node)

    value = bpy.props.FloatProperty(update=update_prop)

    def init(self, context):
        self.index = -3
        self.outputs.new('SdfNodeSocketFloat', "Value")

    def draw_buttons(self, context, layout):
        # create a slider for int values
        layout.prop(self, 'value', text='Float')

    def update(self):
        if self.outputs[0].links:
            tree = bpy.context.space_data.edit_tree
            for link in self.outputs[0].links:
                if link.to_socket.bl_idname in float_category:
                    link.to_socket.default_value = self.value
                else:
                    tree.links.remove(link)
