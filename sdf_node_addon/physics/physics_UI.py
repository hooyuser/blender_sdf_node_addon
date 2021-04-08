import bpy
import numblend as nb
import taichi as ti

from .PBD_stretch_bend import TiClothSimulation
from .PBD_stretch_bend import def_sdf_para
from .PBD_stretch_bend import gen_sdf_taichi

cloth_simulations = []


class ProcessingGeometryOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.processing_geometry_operator"
    bl_label = "Processing Geometry Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene
        ti_device = ti.gpu if scene.sdf_physics.device == 'GPU' else ti.cpu
        ti.init(arch=ti_device, debug=True, default_fp=ti.f32, kernel_profiler=True)
        # gen_sdf_taichi()
        def_sdf_para()
        cloth_simulations.clear()
        cloth_simulations.append(
            TiClothSimulation(scene.sdf_physics))
        return {'FINISHED'}


class SimulateOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simulate_operator"
    bl_label = "Simulate Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        nb.clear_animations()
        nb.init()
        gen_sdf_taichi()
        cloth_simulations[0].reset()
        cloth_simulations[0].animate()
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
        row.label(text="Geometry Processing:")

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
            row.prop(sdf_phy, "enable_LRA")

            if sdf_phy.enable_LRA:
                row = layout.row()
                row.prop_search(sdf_phy,
                                "attach_group",
                                sdf_phy.cloth_obj,
                                "vertex_groups",
                                text="Attach")

        row = layout.row()
        row.prop(sdf_phy, "c_sdf")

        row = layout.row()
        row.prop(sdf_phy, "device")

        row = layout.row()
        row.prop(sdf_phy, "stretch_stiffness")

        row = layout.row()
        row.prop(sdf_phy, "bend_stiffness")

        row = layout.row()
        row.prop(sdf_phy, "ani_para_num")

        if sdf_phy.cloth_obj:
            row = layout.row()
            row.operator("object.processing_geometry_operator",
                         text="Processing")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.label(text="Simulation Settings:")

        row = layout.row()
        row.prop(sdf_phy, "grad_method")

        row = layout.row()
        row.prop(sdf_phy, "analytical_grad")

        row = layout.row()
        row.prop(sdf_phy, "substep_num")

        row = layout.row()
        row.prop(sdf_phy, "solver_num")

        row = layout.row()
        row.prop(sdf_phy, "time_step")

        row = layout.row()
        row.prop(sdf_phy, "drag_damping")

        if sdf_phy.cloth_obj and sdf_phy.c_sdf:
            row = layout.row()
            row.operator("object.simulate_operator", text="Simulate")
