import bpy

from .redrawViewport import Draw

class SdfNodePanel(bpy.types.Panel):
    bl_label = "SDF Node"
    bl_idname = "SDF_PT_NODE_PANEL"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = 'UI'
    bl_category = "Node Tree"
    bl_context = 'objectmode'
    bl_order = 2

    @classmethod
    def poll(cls, context):
        try:
            return context.space_data.node_tree.bl_idname == 'SDFNodeTree'
        except:
            return False

    def draw(self, context):
        sdf_node_data = context.scene.sdf_node_data
        layout = self.layout

        row = layout.row()
        row.label(text=f'Active Viewer: {sdf_node_data.active_viewer}')
        row = layout.row()
        row.label(text=f'Active Collider: {sdf_node_data.active_collider}')


class ViewportRenderOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.viewport_render_operator"
    bl_label = "Viewport Render SDF"
    bl_options = {'REGISTER', 'UNDO'}

    render_sdf_only: bpy.props.BoolProperty(name="Render SDF Only", default=False)

    @classmethod
    def poll(cls, context):
        return context.scene.sdf_node_data.active_viewer

    def execute(self, context):
        Draw.render(context)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "render_sdf_only")


def menu_func(self, context):
        self.layout.operator(ViewportRenderOperator.bl_idname)

bpy.types.VIEW3D_MT_view.append(menu_func)