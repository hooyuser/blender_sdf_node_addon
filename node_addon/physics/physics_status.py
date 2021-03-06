import bpy


class SdfProps(bpy.types.PropertyGroup):
    cloth_obj: bpy.props.PointerProperty(name="Cloth",
                                         type=bpy.types.Object,
                                         description="Cloth Mesh")
    pin_group: bpy.props.StringProperty(name="Pin Vertex Group")
    attach_group: bpy.props.StringProperty(name="Attachment Vertex Group")
    c_obj: bpy.props.PointerProperty(name="Collision",
                                     type=bpy.types.Object,
                                     description="Collision Mesh")
    device: bpy.props.EnumProperty(name="Device",
                                   items=[('GPU', 'GPU', 'GPU'),
                                          ('CPU', 'CPU', 'CPU')],
                                   default="GPU")
