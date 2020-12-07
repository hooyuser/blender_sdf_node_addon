import bpy

from ...base_types.base_node import CustomNode


class RoundNode(bpy.types.Node, CustomNode):
    '''Round node'''

    bl_idname = 'Round'
    bl_label = 'Round'
    bl_icon = 'MOD_CAST'

    def init(self, context):

        self.inputs.new('SdfNodeSocketPositiveFloat', "Radius")
        self.inputs[0].default_value = 0.1

        self.inputs.new('NodeSocketFloat', "Distance")
        self.inputs[1].hide_value = True

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        me = self.index
        if self.inputs[1].links:
            last = self.inputs[1].links[0].from_node.index
            r = self.inputs[0].default_value

            return f'''
                vec3 p_{last} = p_{me};
            ''', f'''
                float d_{me} = d_{last} - {r};
            '''
        else:
            return '', f'''
                float d_{me} = 2 * MAX_DIST;
            '''
