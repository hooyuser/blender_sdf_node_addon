import bpy
from ...base_types.base_node import CustomNode


class SphereSDFNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'SphereSDF'
    bl_label = 'Sphere SDF'
    bl_icon = 'SPHERE'

    def init(self, context):
        self.index = -1

        self.inputs.new('SdfNodeSocketPositiveFloat', "Radius")
        self.inputs[0].default_value = 1

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        loc = self.inputs[1].default_value
        return '', '''
            float d_{}=length(p_{}-vec3({},{},{}))-{};
        '''.format(self.index, self.index, loc[0], loc[1], loc[2],
                   self.inputs[0].default_value)
