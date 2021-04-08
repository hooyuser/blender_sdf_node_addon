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
    grad_method: bpy.props.EnumProperty(name="Gradient",
                                        items=[('Auto', 'Auto', 'Auto'),
                                               ('Numerical', 'Numerical',
                                                'Numerical')],
                                        default="Numerical")

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
                                          description="Damping",
                                          default=1.0,
                                          min=0,
                                          max=10000)

    stretch_stiffness: bpy.props.FloatProperty(
        name="Stretching Stiffness",
        description="Stretching Stiffness",
        default=0.9,
        min=0.001,
        max=1)

    bend_stiffness: bpy.props.FloatProperty(name="Bending Stiffness",
                                            description="Bending Stiffness",
                                            default=0.7,
                                            min=0.001,
                                            max=1)

    analytical_grad: bpy.props.BoolProperty(
        name="Try Using Analytical Gradient",
        description="Use analytical gradient when possible",
        default=True)
