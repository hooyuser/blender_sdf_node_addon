import bpy
from ..redrawViewport import Draw


class CustomNode(object):
    # this line makes the node visible only to the 'CustomNodeTree'
    #   node tree, essentially checking context
    bpy.types.Node.index = bpy.props.IntProperty()

    # ref_num actually equals the referencing number - 1
    bpy.types.Node.ref_num = bpy.props.IntProperty()

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CustomNodeTree'

    def update(self):

        if self.outputs:
            tree = bpy.context.space_data.edit_tree
            if self.outputs[0].links:
                to_node = self.outputs[0].links[0].to_node
                for link in self.outputs[0].links:
                    if link.to_socket.bl_idname != 'NodeSocketFloat':
                        tree.links.remove(link)
                tree.links.new(self.outputs[0],
                               to_node.inputs[-1]).is_valid = True

        Draw.update_callback()
        self.last_update = self
