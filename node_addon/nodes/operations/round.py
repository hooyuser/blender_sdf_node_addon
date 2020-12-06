import bpy

from ...base_types.base_node import CustomNode


class RoundNode(bpy.types.Node, CustomNode):
    '''Round node'''

    bl_idname = 'Round'
    bl_label = 'Round'
    bl_icon = 'MOD_CAST'

    def init(self, context):

        self.inputs.new('SdfNodeSocketFloat', "Radius")
        self.inputs[0].default_value = 0.1

        self.inputs.new('NodeSocketFloat', "Distance")
        self.inputs[1].hide_value = True

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        glsl_code = '''
        float d_%d = d_%d - %f;
        ''' % (self.index, bpy.data.node_groups["NodeTree"].nodes[
            self.inputs[1].links[0].from_node.name].index,
               self.inputs[0].default_value)

        return glsl_code
