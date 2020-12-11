import bpy
from ...base_types.base_node import CustomNode


class CylinderSDFNode(bpy.types.Node, CustomNode):
    '''Cylinder SDF node'''

    bl_idname = 'CylinderSDF'
    bl_label = 'Cylinder SDF'
    bl_icon = 'MESH_CYLINDER'

    def init(self, context):

        self.inputs.new('SdfNodeSocketPositiveFloat', "Height")
        self.inputs[0].default_value = 2

        self.inputs.new('SdfNodeSocketPositiveFloat', "Radius")
        self.inputs[1].default_value = 1

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):
        loc = self.inputs[2].default_value
        h = self.inputs[0].default_value
        r = self.inputs[1].default_value
        return f'''
            float f_{self.index}(vec3 p){{
                vec2 e = abs(vec2(length(p.xz-vec2({loc[0]},{loc[2]})),p.y-({loc[1]}))) - vec2({r},{h});
                return min(max(e.x,e.y),0.0) + length(max(e,0.0));
            }}
            '''

    def gen_glsl(self, ref_stack):
        me = self.index
        return '', f'''
            float d_{me}_{self.ref_num}=f_{me}(p_{me}_{self.ref_num});
        '''
