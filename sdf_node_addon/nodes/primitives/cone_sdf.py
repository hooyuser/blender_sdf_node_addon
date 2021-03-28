import bpy
from ...base_types.base_node import CustomNode


class ConeSDFNode(bpy.types.Node, CustomNode):
    '''Cone SDF node'''

    bl_idname = 'ConeSDF'
    bl_label = 'Cone SDF'
    bl_icon = 'CONE'

    def init(self, context):

        self.inputs.new('SdfNodeSocketPositiveFloat', "Height")
        self.inputs[0].default_value = 2

        self.inputs.new('SdfNodeSocketPositiveFloat', "Angle")
        self.inputs[1].default_value = 30

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):
        loc = self.inputs[2].default_value
        return f'''
            float f_{self.index}(vec3 p){{
                vec2 q = {self.inputs[0].default_value} * vec2(tan(radians({self.inputs[1].default_value})),-1.0);
                vec2 w = vec2(length(p.xz-vec2({loc[0]},{loc[2]})), p.y-({loc[1]}));
                vec2 a = w - q*clamp(dot(w,q)/dot(q,q), 0.0, 1.0);
                vec2 b = w - q*vec2(clamp( w.x/q.x, 0.0, 1.0 ), 1.0);
                float k = sign( q.y );
                float t = min(dot( a, a ),dot(b, b));
                float s = max( k*(w.x*q.y-w.y*q.x),k*(w.y-q.y));
                return sqrt(t)*sign(s);
            }}
            '''

    def gen_glsl(self, ref_stack):
        me = self.index
        return '', f'''
            float d_{me}_{self.ref_num}=f_{me}(p_{me}_{self.ref_num});
        '''
