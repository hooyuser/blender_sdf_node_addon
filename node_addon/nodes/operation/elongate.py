import bpy
from ...base_types.base_node import CustomNode


class ElongateNode(bpy.types.Node, CustomNode):
    '''Elongate node'''

    bl_idname = 'Elongate'
    bl_label = 'Elongate'
    bl_icon = 'SNAP_MIDPOINT'

    def init(self, context):
        self.inputs.new('SdfNodeSocketVectorTranslation', "Shift")

        self.inputs.new('NodeSocketFloat', "SDF")
        self.inputs[1].hide_value = True

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):
        if self.inputs[1].links:
            h = self.inputs[0].default_value
            return f'''vec3 g_{self.index}(vec3 p){{
                    return p - clamp( p, -vec3({h[0]},{h[1]},{h[2]}), vec3({h[0]},{h[1]},{h[2]}));
                }}
                '''
        else:
            return ''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num
        if self.inputs[1].links:
            last_node = self.inputs[1].links[0].from_node
            last = last_node.index
            last_ref = ref_stacks[last].pop()

            glsl_p = f'''
                vec3 p_{last}_{last_ref} = g_{me}(p_{me}_{ref_i});
            '''
            glsl_d = f'''
                float d_{me}_{ref_i}=d_{last}_{last_ref};
            '''
        else:
            glsl_p = ''
            glsl_d = f'''
                float d_{me}_{ref_i} = 2 * MAX_DIST;
            '''

        return glsl_p, glsl_d
