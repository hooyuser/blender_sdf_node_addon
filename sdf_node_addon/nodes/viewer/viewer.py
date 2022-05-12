import inspect

import bpy

from ...base_types.base_node import CustomNode
from ...redrawViewport import Draw


class OutputGLSLOperator(bpy.types.Operator):

    bl_idname = "wm.output_glsl"
    bl_label = "Minimal Operator"

    def execute(self, context):
        sdf_text = bpy.data.texts.new("sdf.glsl")
        sdf_text.clear()
        shader_code = inspect.cleandoc(Draw.frag_shader_code)
        sdf_text.write(shader_code)
        return {'FINISHED'}


class ViewerNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'Viewer'
    bl_label = 'Viewer'
    bl_icon = 'RESTRICT_RENDER_OFF'

    def update_show(self, context):
        if self.enabled_show:
            for node in bpy.context.space_data.edit_tree.nodes:
                if node.bl_idname == 'Viewer' and node.name != self.name:
                    node.enabled_show = False
            context.scene.sdf_node_data.active_viewer = self.name
        elif context.scene.sdf_node_data.active_viewer == self.name:
            context.scene.sdf_node_data.active_viewer = ''
        # Draw.refreshViewport(self.enabled_show)

    def update_collision(self, context):
        if self.enabled_collision:
            for node in bpy.context.space_data.edit_tree.nodes:
                if node.bl_idname == 'Viewer' and node.name != self.name:
                    node.enabled_collision = False
            context.scene.sdf_node_data.active_collider = self.name
        elif context.scene.sdf_node_data.active_collider == self.name:
            context.scene.sdf_node_data.active_collider = ''

    enabled_show: bpy.props.BoolProperty(name="Enabled_show",
                                         default=False,
                                         update=update_show)

    enabled_collision: bpy.props.BoolProperty(name="Enabled_collision",
                                              default=False,
                                              update=update_collision)

    def update(self):  # rewrite update function
        if not self.inputs[
                0].links and bpy.context.scene.sdf_node_data.active_viewer == self.name:
            Draw.refreshViewport(False)

    def draw_buttons(self, context, layout):
        layout.prop(self, "enabled_show", text="Show SDF")
        layout.prop(self, "enabled_collision", text="Collision")
        layout.operator("wm.output_glsl", text='Output GLSL')

    def init(self, context):
        self.inputs.new('SdfNodeSocketSdf', "SDF")
        self.inputs[0].hide_value = True

    def free(self):
        if bpy.context.scene.sdf_node_data.active_viewer == self.name:
            bpy.context.scene.sdf_node_data.active_viewer = ''
        if bpy.context.scene.sdf_node_data.active_collider == self.name:
            bpy.context.scene.sdf_node_data.active_collider = ''
        Draw.refreshViewport(False)

    def copy(self, node):
        self.enabled_show = False
        self.enabled_collision = False
