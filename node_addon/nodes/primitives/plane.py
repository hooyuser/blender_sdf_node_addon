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

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl_func(self):
        loc = self.inputs[2].default_value
        n = self.inputs[0].default_value

        return f'''
            float f_{self.index}(vec3 p){{
                return dot(p-vec3({loc[0]},{loc[1]},{loc[2]}),
                    vec3({n[0]},{n[1]},{n[2]})) + ({self.inputs[1].default_value});
            }}
            '''

    def gen_glsl(self, ref_stack):
        me = self.index
        return '', f'''
            float d_{me}_{self.ref_num}=f_{me}(p_{me}_{self.ref_num});
        '''
