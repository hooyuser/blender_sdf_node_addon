import bpy
import mathutils

from ...base_types.base_node import CustomNode


class TransformNode(bpy.types.Node, CustomNode):
    '''Transform node'''

    bl_idname = 'Transform'
    bl_label = 'Transform'
    bl_icon = 'OBJECT_ORIGIN'

    def init(self, context):
        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")
        self.inputs.new('SdfNodeSocketEuler', "Rotation")
        self.inputs.new('SdfNodeSocketFloat', "Scale")
        self.inputs[2].default_value = 1

        self.inputs.new('NodeSocketFloat', "SDF")
        self.inputs[3].hide_value = True

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):
        me = self.index
        if self.inputs[3].links:
            eul = self.inputs[1].default_value
            mat_rot = eul.to_matrix()
            mat_loc = mathutils.Matrix.Translation(
                self.inputs[0].default_value)
            sca = self.inputs[2].default_value
            mat = mat_loc @ mat_rot.to_4x4()
            mathutils.Matrix.invert(mat)
            return f'''vec3 g_{me}(vec3 p){{
                    return vec3(p.x*{mat[0][0]}+p.y*{mat[0][1]}+p.z*{mat[0][2]}+({mat[0][3]}),
                        p.x*{mat[1][0]}+p.y*{mat[1][1]}+p.z*{mat[1][2]}+({mat[1][3]}),
                        p.x*{mat[2][0]}+p.y*{mat[2][1]}+p.z*{mat[2][2]}+({mat[2][3]}))/({sca});
                }}
                float f_{me}(float d){{
                    return d * abs({sca});
                }}
                '''
        else:
            return ''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num
        if self.inputs[3].links:
            last_node = self.inputs[3].links[0].from_node
            last = last_node.index
            last_ref = ref_stacks[last].pop()

            glsl_p = f'''
                vec3 p_{last}_{last_ref} = g_{me}(p_{me}_{ref_i});
            '''
            glsl_d = f'''
                float d_{me}_{ref_i}=f_{me}(d_{last}_{last_ref});
            '''
        else:
            glsl_p = ''
            glsl_d = f'''
                float d_{me}_{ref_i} = 2 * MAX_DIST;
            '''

        return glsl_p, glsl_d
