import bpy
from ...base_types.base_node import CustomNode


class OnionNode(bpy.types.Node, CustomNode):
    '''Onion node'''

    bl_idname = 'Onion'
    bl_label = 'Onion'
    bl_icon = 'MOD_CAST'

    def init(self, context):

        self.inputs.new('SdfNodeSocketPositiveFloat', "Thickness")
        self.inputs[0].default_value = 0.1

        self.inputs.new('NodeSocketFloat', "Distance")
        self.inputs[1].hide_value = True

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self, node_info):
        last = self.inputs[1].links[0].from_node.index
        me = self.index
        r = self.inputs[0].default_value

        node_info.glsl_p_list.append(f'''
            vec3 p_{last} = p_{me};
        ''')

        node_info.glsl_d_list.append(f'''
            float d_{me} = abs(d_{last}) - {r};
        ''')
