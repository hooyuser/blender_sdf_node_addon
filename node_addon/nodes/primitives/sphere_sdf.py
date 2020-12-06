import bpy
from ...base_types.base_node import CustomNode


class SphereSDFNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'SphereSDF'
    bl_label = 'Sphere SDF'
    bl_icon = 'PLUS'

    def init(self, context):
        self.index = -1

        self.inputs.new('SdfNodeSocketFloat', "Radius")
        self.inputs[0].default_value = 1

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        loc = self.inputs[1].default_value
        glsl_code = '''
            float d_{}=length(p-vec3({},{},{}))-{};
        '''.format(self.index, loc[0], loc[1], loc[2],
                   self.inputs[0].default_value)

        return glsl_code
