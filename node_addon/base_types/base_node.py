import bpy
from ..redrawViewport import Draw


class CustomNode(object):
    # this line makes the node visible only to the 'CustomNodeTree'
    #   node tree, essentially checking context
    bpy.types.Node.index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CustomNodeTree'

    def update(self):
        Draw.update_callback()
