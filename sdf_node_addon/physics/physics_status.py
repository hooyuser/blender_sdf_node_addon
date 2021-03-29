import bpy


def scene_mychosenobject_poll(self, nodeTree):
    return nodeTree.bl_idname == 'SDFNodeTree'


class SdfPhyProps(bpy.types.PropertyGroup):
    cloth_obj: bpy.props.PointerProperty(name="Cloth",
                                         type=bpy.types.Object,
                                         description="Cloth Mesh")
    pin_group: bpy.props.StringProperty(name="Pin Vertex Group")
    enable_LRA: bpy.props.BoolProperty(
        name="LRA Constraints",
        description="Long Range Attachments Constraints",
        default=False)
    attach_group: bpy.props.StringProperty(name="Attachments Vertex Group")
    # c_obj: bpy.props.PointerProperty(name="Collision",
    #                                  type=bpy.types.Object,
    #                                  description="Collision Mesh")
    c_sdf: bpy.props.PointerProperty(name="SDF",
                                     type=bpy.types.NodeTree,
                                     description="Collision SDF",
                                     poll=scene_mychosenobject_poll)
    device: bpy.props.EnumProperty(name="Device",
                                   items=[('GPU', 'GPU', 'GPU'),
                                          ('CPU', 'CPU', 'CPU')],
                                   default="CPU")
    ani_para_num: bpy.props.IntProperty(
        name="Parameters",
        description="The number of animated parameters",
        default=50,
        min=1,
        max=1000)
    substep_num: bpy.props.IntProperty(name="Substeps",
                                       description="Substeps Per Frame",
                                       default=10,
                                       min=1,
                                       max=200)
    solver_num: bpy.props.IntProperty(name="Solver Iterations",
                                      description="Solver Iterations",
                                      default=20,
                                      min=1,
                                      max=400)
    time_step: bpy.props.FloatProperty(name="Time Step (ms)",
                                       description="Time Step (ms)",
                                       default=1,
                                       min=0,
                                       max=1000)

    drag_damping: bpy.props.FloatProperty(name="Damping",
                                          description="Solver Iterations",
                                          default=1.0,
                                          min=0,
                                          max=10000)

    # sdf_para_changed: bpy.props.BoolProperty(
    #     name="SDF_para_changed",
    #     description="SDF parameters changed",
    #     default=True)
