import bpy

from ...base_types.base_node import CustomNode
from ...base_types.base_material_node import BaseMaterialNode


class PBRMaterialNode(bpy.types.Node, CustomNode, BaseMaterialNode):
    '''PBR Material node'''

    bl_idname = 'PBRMaterial'
    bl_label = 'PBR Material'
    bl_icon = 'MOD_BEVEL'

    def init(self, context):
        self.inputs.new('SdfNodeSocketColor', "Base Color")

        self.inputs.new('SdfNodeSocketNormalizedFloat', "Metalness")

        self.inputs.new('SdfNodeSocketNormalizedFloat', "Roughness")
        self.inputs[2].default_value = 0.5

        self.inputs.new('SdfNodeSocketNormalizedFloat', "Specular")
        self.inputs[3].default_value = 0.5

        self.inputs.new('SdfNodeSocketSdf', "SDF")
        self.inputs[-1].hide_value = True

        self.outputs.new('SdfNodeSocketSdf', "SDF")

    def gen_glsl_func(self):
        return ''

    def gen_glsl(self, ref_stacks):
        me = self.index
        ref_i = self.ref_num
        if self.inputs[-1].links:
            last_node = self.inputs[-1].links[0].from_node
            last = last_node.index
            last_ref = ref_stacks[last].pop()

            glsl_p = f'''
    vec3 p_{last}_{last_ref} = p_{me}_{ref_i};
'''
            #             glsl_d = f'''
            #     SDFInfo d_{me}_{ref_i} = SDFInfo(d_{last}_{last_ref}.sd, {self.material_id});
            # '''
            glsl_d = f'''
    SDFInfo d_{me}_{ref_i} = SDFInfo(d_{last}_{last_ref}.sd, {self.material_id}); 
'''
        else:
            glsl_p = ''
            glsl_d = f'''
                SDFInfo d_{me}_{ref_i} = SDFInfo(2.0 * MAX_DIST, 0);
            '''

        return glsl_p, glsl_d

    def gen_glsl_material(self):

        r, g, b = self.inputs[0].default_value
        return f'PBRMaterial(vec3({r}, {g}, {b}), {self.inputs[1].default_value}, {self.inputs[2].default_value}, {self.inputs[3].default_value})'
