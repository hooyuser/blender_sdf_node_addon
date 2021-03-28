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

        self.outputs.new('NodeSocketFloat', "SDF")

        self.width = 153

    def gen_glsl_func(self):
        loc = self.inputs[2].default_value

        return f'''
            float f_{self.index}(vec3 p){{
                return length(vec2(length(p.xz-vec2({loc[0]},{loc[2]}))-
                    {self.inputs[0].default_value},p.y-({loc[1]})))-{self.inputs[1].default_value};
            }}
            '''

    def gen_glsl(self, ref_stack):
        me = self.index
        return '', f'''
            float d_{me}_{self.ref_num}=f_{me}(p_{me}_{self.ref_num});
        '''
