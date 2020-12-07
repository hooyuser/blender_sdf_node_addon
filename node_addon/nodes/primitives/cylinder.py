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

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self, node_info):
        loc = self.inputs[2].default_value
        h = self.inputs[0].default_value
        r = self.inputs[1].default_value
        me = self.index
        node_info.glsl_p_list.append('')
        node_info.glsl_d_list.append(f'''
            vec2 e_{me} = abs(vec2(length(p_{me}.xz-vec2({loc[0]},{loc[2]})),p_{me}.y-({loc[1]}))) - vec2({r},{h});
            float d_{me} = min(max(e_{me}.x,e_{me}.y),0.0) + length(max(e_{me},0.0));
        ''')
