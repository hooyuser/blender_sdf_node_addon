import bpy
from ...base_types.base_node import CustomNode


class BoxSDFNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'BoxSDF'
    bl_label = 'Box SDF'
    bl_icon = 'PLUS'

    def init(self, context):

        self.inputs.new('SdfNodeSocketFloat', "Length")
        self.inputs[0].default_value = 1

        self.inputs.new('SdfNodeSocketFloat', "Width")
        self.inputs[1].default_value = 1

        self.inputs.new('SdfNodeSocketFloat', "Height")
        self.inputs[2].default_value = 1

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        loc = self.inputs[3].default_value
        glsl_code = '''
            vec3 q_{} = abs(p - vec3({},{},{})) - vec3({},{},{});
            float d_{} = length(max(q_{},0.0)) +
                min(max(q_{}.x,max(q_{}.y,q_{}.z)),0.0);
        '''.format(self.index, loc[0], loc[1], loc[2],
                   self.inputs[0].default_value, self.inputs[1].default_value,
                   self.inputs[2].default_value, self.index, self.index,
                   self.index, self.index, self.index)

        return glsl_code
