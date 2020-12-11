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

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):
        loc = self.inputs[1].default_value
        return f'''
            float f_{self.index}(vec3 p){{
                return length(p-vec3({loc[0]},{loc[1]},{loc[2]}))-({self.inputs[0].default_value});
            }}
            '''

    def gen_glsl(self, ref_stack):
        me = self.index
        return '', f'''
            float d_{me}_{self.ref_num}=f_{me}(p_{me}_{self.ref_num});
        '''
