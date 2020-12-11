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

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):
        loc = self.inputs[3].default_value
        return f'''
            float f_{self.index}(vec3 p){{
                vec3 q = abs(p - vec3({loc[0]},{loc[1]},{loc[2]})) -
                    vec3({self.inputs[0].default_value},{self.inputs[1].default_value},{self.inputs[2].default_value});
                return length(max(q,0.0)) +
                    min(max(q.x,max(q.y,q.z)),0.0);
            }}
            '''

    def gen_glsl(self, ref_stack):
        me = self.index
        return '', f'''
            float d_{me}_{self.ref_num}=f_{me}(p_{me}_{self.ref_num});
        '''
