import bpy
import numblend as nb
import taichi as ti

from .PBD_stretch_bend_gpu import TiData


class SimulateOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simulate_operator"
    bl_label = "Simulate Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        nb.init()
        scene = context.scene
        ti_device = ti.gpu if scene.sdf_physics.device == 'GPU' else ti.cpu
        ti.init(arch=ti_device, debug=False)
        data = TiData(scene.sdf_physics, scene.frame_end)
        data.animate()
        return {'FINISHED'}


class ClothPhysicsPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "SDF Cloth Physics"
    bl_idname = "OBJECT_PT_CLOTH"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SDF Cloth"
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout

        sdf_phy = context.scene.sdf_physics

        # row = layout.row()
        # row.label(text="Hello world!", icon='WORLD_DATA')

        row = layout.row()
        row.prop(sdf_phy, "cloth_obj")

        if sdf_phy.cloth_obj:
            row = layout.row()
            row.prop_search(sdf_phy,
                            "pin_group",
                            sdf_phy.cloth_obj,
                            "vertex_groups",
                            text="Pin")

            row = layout.row()
            row.prop_search(sdf_phy,
                            "attach_group",
                            sdf_phy.cloth_obj,
                            "vertex_groups",
                            text="Attach")

        row = layout.row()
        row.prop(sdf_phy, "c_obj")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.label(text="Simulation Setting:")

        row = layout.row()
        row.prop(sdf_phy, "device")

        if sdf_phy.cloth_obj and sdf_phy.c_obj:
            row = layout.row()
            row.operator("object.simulate_operator", text="Simulate")
