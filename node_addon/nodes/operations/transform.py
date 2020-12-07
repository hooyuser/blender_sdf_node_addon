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

        self.inputs.new('NodeSocketFloat', "Distance")
        self.inputs[3].hide_value = True

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self, node_info):
        me = self.index
        if self.inputs[3].links:
            last = self.inputs[3].links[0].from_node.index
            eul = self.inputs[1].default_value
            mat_rot = eul.to_matrix()
            mat_loc = mathutils.Matrix.Translation(
                self.inputs[0].default_value)
            sca = self.inputs[2].default_value
            mat = mat_loc @ mat_rot.to_4x4()
            mathutils.Matrix.invert(mat)

            node_info.glsl_p_list.append(f'''
                vec3 p_{last} = vec3(p_{me}.x*{mat[0][0]}+p_{me}.y*{mat[0][1]}+p_{me}.z*{mat[0][2]}+({mat[0][3]}),
                    p_{me}.x*{mat[1][0]}+p_{me}.y*{mat[1][1]}+p_{me}.z*{mat[1][2]}+({mat[1][3]}),
                    p_{me}.x*{mat[2][0]}+p_{me}.y*{mat[2][1]}+p_{me}.z*{mat[2][2]}+({mat[2][3]}))/({sca});
            ''')
            node_info.glsl_d_list.append(f'''
                float d_{me} = d_{last} * abs({sca});
            ''')
        else:
            node_info.glsl_p_list.append('')
            node_info.glsl_d_list.append(f'''
                float d_{me} = 2 * MAX_DIST;
            ''')
