import bpy


class BaseMaterialNode(object):
    bpy.types.Node.material_id = bpy.props.IntProperty()
