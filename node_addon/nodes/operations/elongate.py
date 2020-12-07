import bpy
from ...base_types.base_node import CustomNode


class ElongateNode(bpy.types.Node, CustomNode):
    '''Elongate node'''

    bl_idname = 'Elongate'
    bl_label = 'Elongate'
    bl_icon = 'MOD_MIRROR'

    def init(self, context):
        self.inputs.new('SdfNodeSocketVectorTranslation', "Shift")

        self.inputs.new('NodeSocketFloat', "Distance")
        self.inputs[1].hide_value = True

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self, node_info):
        if self.inputs[1].links:
            last = self.inputs[1].links[0].from_node.index
            me = self.index
            h = self.inputs[0].default_value
            node_info.glsl_p_list.append(f'''
                vec3 p_{last} = p_{me} - clamp( p_{me}, -vec3({h[0]},{h[1]},{h[2]}), vec3({h[0]},{h[1]},{h[2]}));
            ''')
            node_info.glsl_d_list.append(f'''
                float d_{me} = d_{last};
            ''')
        else:
            node_info.glsl_p_list.append('')
            node_info.glsl_d_list.append(f'''
                float d_{me} = 2 * MAX_DIST;
            ''')
