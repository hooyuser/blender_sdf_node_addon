import bpy


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
