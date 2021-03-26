import bpy


class Status(object):
    active_nodetree = None  # bpy.context.space_data.edit_tree
    active_viewer = None
    show_SDF = False

    @staticmethod
    def exist_node_tree():
        for node_tree in bpy.data.node_groups:
            if node_tree.bl_idname == 'SDFNodeTree':
                return True
        return False

    @staticmethod
    def exist_viewer():
        for node_tree in bpy.data.node_groups:
            if node_tree.bl_idname == 'SDFNodeTree':
                for node in node_tree.nodes:
                    if node.bl_idname == 'Viewer':
                        return True
        return False

    @classmethod
    def active_nodetree(cls):
        if Status.exist_node_tree():
            if bpy.context.space_data:
                cls.active_nodetree = bpy.context.space_data.edit_tree.name
            return cls.active_nodetree
        return None
