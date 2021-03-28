import bpy
from ..redrawViewport import Draw
from ..physics.PBD_stretch_bend import gen_sdf_taichi


class CustomNode(object):
    # this line makes the node visible only to the 'SDFNodeTree'
    #   node tree, essentially checking context
    bpy.types.Node.index = bpy.props.IntProperty()
    bpy.types.Node.coll_index = bpy.props.IntProperty()
    # index = -1: to be searched. index = -2: will not be searched

    bpy.types.Node.ref_num = bpy.props.IntProperty()
    bpy.types.Node.coll_ref_num = bpy.props.IntProperty()
    # ref_num actually equals the referencing number - 1

    bpy.types.Node.coll_para_idx = bpy.props.IntProperty()
    # the index of the first parameter of a node

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SDFNodeTree'

    def update(self):
        if self.outputs:
            tree = bpy.context.space_data.edit_tree
            if self.outputs[0].links:
                for link in self.outputs[0].links:
                    to_node = link.to_node
                    if link.to_socket.bl_idname != 'NodeSocketFloat':
                        tree.links.remove(link)
                        tree.links.new(self.outputs[0],
                                       to_node.inputs[-1]).is_valid = True
        Draw.update_callback()
        gen_sdf_taichi()

        # self.last_update = self
