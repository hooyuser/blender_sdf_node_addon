import bpy

from ...base_types.base_node import CustomNode


class SimplexNoiseNode(bpy.types.Node, CustomNode):
    '''Simplex Noise node'''

    bl_idname = 'SimplexNoise'
    bl_label = 'Simplex Noise'
    bl_icon = 'MOD_BEVEL'

    def init(self, context):
        self.inputs.new('SdfNodeSocketFloat', "Magnitude")
        self.inputs[0].default_value = 1
        self.inputs.new('SdfNodeSocketFloat', "Time")
        self.inputs.new('SdfNodeSocketFloat', "X Offset")
        self.inputs.new('SdfNodeSocketFloat', "Y Offset")
        self.inputs.new('SdfNodeSocketFloat', "Z Offset")

        self.inputs.new('NodeSocketFloat', "SDF")
        self.inputs[5].hide_value = True

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):
        if self.inputs[5].links:
            k = self.inputs[0].default_value
            t = self.inputs[1].default_value
            x = self.inputs[2].default_value
            y = self.inputs[3].default_value
            z = self.inputs[4].default_value

            return f'''
                float f_{self.index}(float d, vec3 p){{
                    vec4 gradient = vec4(0.0);
                    vec4 v = vec4(p+vec3({x},{y},{z}),{t});
                    const vec4  C = vec4( 0.138196601125011,  // (5 - sqrt(5))/20  G4
                                            0.276393202250021,  // 2 * G4
                                            0.414589803375032,  // 3 * G4
                                        -0.447213595499958); // -1 + 4 * G4

                    // First corner
                    vec4 i  = floor(v + dot(v, vec4(F4)) );
                    vec4 x0 = v -   i + dot(i, C.xxxx);

                    // Other corners

                    // Rank sorting originally contributed by Bill Licea-Kane, AMD (formerly ATI)
                    vec4 i0;
                    vec3 isX = step( x0.yzw, x0.xxx );
                    vec3 isYZ = step( x0.zww, x0.yyz );
                    //  i0.x = dot( isX, vec3( 1.0 ) );
                    i0.x = isX.x + isX.y + isX.z;
                    i0.yzw = 1.0 - isX;
                    //  i0.y += dot( isYZ.xy, vec2( 1.0 ) );
                    i0.y += isYZ.x + isYZ.y;
                    i0.zw += 1.0 - isYZ.xy;
                    i0.z += isYZ.z;
                    i0.w += 1.0 - isYZ.z;

                    // i0 now contains the unique values 0,1,2,3 in each channel
                    vec4 i3 = clamp( i0, 0.0, 1.0 );
                    vec4 i2 = clamp( i0-1.0, 0.0, 1.0 );
                    vec4 i1 = clamp( i0-2.0, 0.0, 1.0 );

                    //  x0 = x0 - 0.0 + 0.0 * C.xxxx
                    //  x1 = x0 - i1  + 1.0 * C.xxxx
                    //  x2 = x0 - i2  + 2.0 * C.xxxx
                    //  x3 = x0 - i3  + 3.0 * C.xxxx
                    //  x4 = x0 - 1.0 + 4.0 * C.xxxx
                    vec4 x1 = x0 - i1 + C.xxxx;
                    vec4 x2 = x0 - i2 + C.yyyy;
                    vec4 x3 = x0 - i3 + C.zzzz;
                    vec4 x4 = x0 + C.wwww;

                    // Permutations
                    i = mod289(i);
                    float j0 = permute( permute( permute( permute(i.w) + i.z) + i.y) + i.x);
                    vec4 j1 = permute( permute( permute( permute (
                                i.w + vec4(i1.w, i2.w, i3.w, 1.0 ))
                            + i.z + vec4(i1.z, i2.z, i3.z, 1.0 ))
                            + i.y + vec4(i1.y, i2.y, i3.y, 1.0 ))
                            + i.x + vec4(i1.x, i2.x, i3.x, 1.0 ));

                    // Gradients: 7x7x6 points over a cube, mapped onto a 4-cross polytope
                    // 7*7*6 = 294, which is close to the ring size 17*17 = 289.
                    vec4 ip = vec4(1.0/294.0, 1.0/49.0, 1.0/7.0, 0.0) ;

                    vec4 p0 = grad4(j0,   ip);
                    vec4 p1 = grad4(j1.x, ip);
                    vec4 p2 = grad4(j1.y, ip);
                    vec4 p3 = grad4(j1.z, ip);
                    vec4 p4 = grad4(j1.w, ip);

                    // Normalise gradients
                    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
                    p0 *= norm.x;
                    p1 *= norm.y;
                    p2 *= norm.z;
                    p3 *= norm.w;
                    p4 *= taylorInvSqrt(dot(p4,p4));

                    // Mix contributions from the five corners
                    vec3 m0 = max(0.5 - vec3(dot(x0,x0), dot(x1,x1), dot(x2,x2)), 0.0);
                    vec2 m1 = max(0.5 - vec2(dot(x3,x3), dot(x4,x4)            ), 0.0);
                    vec3  m02 = m0 * m0;
                    vec2 m12 = m1 * m1;
                    vec3 m04 = m02 * m02;
                    vec2 m14 = m12 * m12;
                    vec3 pdotx0 = vec3(dot(p0,x0), dot(p1,x1), dot(p2,x2));
                    vec2 pdotx1 = vec2(dot(p3,x3), dot(p4,x4));

                    // Determine noise gradient;
                    vec3 temp0 = m02 * m0 * pdotx0;
                    vec2 temp1 = m12 * m1 * pdotx1;
                    gradient = -8.0 * (temp0.x * x0 + temp0.y * x1 + temp0.z * x2 + temp1.x * x3 + temp1.y * x4);
                    gradient += m04.x * p0 + m04  .y * p1 + m04.z * p2 + m14.x * p3 + m14.y * p4;
                    gradient *= 109.319;

                    return d + ({k}) * 10.9319 * (  dot(m02*m02, vec3( dot( p0, x0 ), dot( p1, x1 ), dot( p2, x2 )))
                        + dot(m12*m12, vec2( dot( p3, x3 ), dot( p4, x4 ) ) ) ) ;
                }}
                '''
        else:
            return ''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num
        if self.inputs[5].links:
            last_node = self.inputs[5].links[0].from_node
            last = last_node.index
            last_ref = ref_stacks[last].pop()

            glsl_p = f'''
                vec3 p_{last}_{last_ref} = p_{me}_{ref_i};
            '''
            glsl_d = f'''
                float d_{me}_{ref_i}=f_{me}(d_{last}_{last_ref}, p);
            '''
        else:
            glsl_p = ''
            glsl_d = f'''
                float d_{me}_{ref_i} = 2 * MAX_DIST;
            '''

        return glsl_p, glsl_d
