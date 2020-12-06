import bpy
from ...base_types.base_node import CustomNode


class ConeSDFNode(bpy.types.Node, CustomNode):
    '''Cone SDF node'''

    bl_idname = 'ConeSDF'
    bl_label = 'Cone SDF'
    bl_icon = 'CONE'

    def init(self, context):

        self.inputs.new('SdfNodeSocketFloat', "Height")
        self.inputs[0].default_value = 2

        self.inputs.new('SdfNodeSocketFloat', "Angle")
        self.inputs[1].default_value = 30

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        loc = self.inputs[2].default_value
        glsl_code = '''
            vec2 q_%(i)d = %(h)f * vec2(tan(radians(%(angle)f)),-1.0);
            vec2 w_%(i)d = vec2( length(p.xz-vec2(%(x)f,%(z)f)), p.y-(%(y)f));
            vec2 a_%(i)d = w_%(i)d - q_%(i)d*clamp(dot(w_%(i)d,q_%(i)d)/dot(q_%(i)d,q_%(i)d), 0.0, 1.0);
            vec2 b_%(i)d = w_%(i)d - q_%(i)d*vec2(clamp( w_%(i)d.x/q_%(i)d.x, 0.0, 1.0 ), 1.0);
            float k_%(i)d = sign( q_%(i)d.y );
            float t_%(i)d = min(dot( a_%(i)d, a_%(i)d ),dot(b_%(i)d, b_%(i)d));
            float s_%(i)d = max( k_%(i)d*(w_%(i)d.x*q_%(i)d.y-w_%(i)d.y*q_%(i)d.x),k_%(i)d*(w_%(i)d.y-q_%(i)d.y));
            float d_%(i)d = sqrt(t_%(i)d)*sign(s_%(i)d);
        ''' % {
            'i': self.index,
            'h': self.inputs[0].default_value,
            'angle': self.inputs[1].default_value,
            'x': loc[0],
            'y': loc[1],
            'z': loc[2]
        }

        return glsl_code
