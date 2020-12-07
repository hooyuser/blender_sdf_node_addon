import bpy
from ...base_types.base_node import CustomNode


class PlaneSDFNode(bpy.types.Node, CustomNode):
    '''Plane SDF node'''

    bl_idname = 'PlaneSDF'
    bl_label = 'Plane SDF'
    bl_icon = 'MESH_PLANE'

    def init(self, context):

        self.inputs.new('SdfNodeSocketFloatVector', "Normal")
        self.inputs[0].default_value = (0, 0, 1)

        self.inputs.new('SdfNodeSocketFloat', "Intercept")
        self.inputs[1].default_value = 10

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self, node_info):
        loc = self.inputs[2].default_value
        n = self.inputs[0].default_value
        me = self.index
        node_info.glsl_p_list.append('')
        node_info.glsl_d_list.append(f'''
            float d_{me} = dot(p_{me}-vec3({loc[0]},{loc[1]},{loc[2]}),
                vec3({n[0]},{n[1]},{n[2]})) + {self.inputs[1].default_value};
        ''')
