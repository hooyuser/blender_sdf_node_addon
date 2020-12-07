import bpy
from ...base_types.base_node import CustomNode


class BoxSDFNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'BoxSDF'
    bl_label = 'Box SDF'
    bl_icon = 'CUBE'

    def init(self, context):

        self.inputs.new('SdfNodeSocketPositiveFloat', "Length")
        self.inputs[0].default_value = 1

        self.inputs.new('SdfNodeSocketPositiveFloat', "Width")
        self.inputs[1].default_value = 1

        self.inputs.new('SdfNodeSocketPositiveFloat', "Height")
        self.inputs[2].default_value = 1

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self, node_info):
        loc = self.inputs[3].default_value
        me = self.index
        node_info.glsl_p_list.append('')
        node_info.glsl_d_list.append(f'''
            vec3 q_{me} = abs(p_{me} - vec3({loc[0]},{loc[1]},{loc[2]})) -
                vec3({self.inputs[0].default_value},{self.inputs[1].default_value},{self.inputs[2].default_value});
            float d_{me} = length(max(q_{me},0.0)) +
                min(max(q_{me}.x,max(q_{me}.y,q_{me}.z)),0.0);
        ''')
