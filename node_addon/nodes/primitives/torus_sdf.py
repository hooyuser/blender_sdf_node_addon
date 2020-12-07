import bpy
from ...base_types.base_node import CustomNode


class TorusSDFNode(bpy.types.Node, CustomNode):
    '''Torus SDF node'''

    bl_idname = 'TorusSDF'
    bl_label = 'Torus SDF'
    bl_icon = 'MESH_TORUS'

    def init(self, context):

        self.inputs.new('SdfNodeSocketPositiveFloat', "Major Radius")
        self.inputs[0].default_value = 2

        self.inputs.new('SdfNodeSocketPositiveFloat', "Minor Radius")
        self.inputs[1].default_value = 1

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        loc = self.inputs[2].default_value
        return '', f'''
            float d_{self.index} = length(vec2(length(p.xz-vec2({loc[0]},{loc[2]}))-
                {self.inputs[0].default_value},p.y-({loc[1]})))-{self.inputs[1].default_value};
        '''
