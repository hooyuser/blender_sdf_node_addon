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
        Draw.update_callback()
