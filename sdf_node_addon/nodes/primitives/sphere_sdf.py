import bpy
from ...base_types.base_node import CustomNode


class SphereSDFNode(bpy.types.Node, CustomNode):
    '''A simple input node'''

    bl_idname = 'SphereSDF'
    bl_label = 'Sphere SDF'
    bl_icon = 'SPHERE'
    para_num = 4

    def init(self, context):
        self.index = -1
        self.coll_index = -1  # index for collision system

        self.inputs.new('SdfNodeSocketPositiveFloat', "Radius")
        self.inputs[0].default_value = 1

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "SDF")

    def get_para(self, idx):
        return [
            self.inputs[0].default_value, self.inputs[1].default_value[0],
            self.inputs[1].default_value[1], self.inputs[1].default_value[2]
        ][idx]

    def gen_glsl_func(self):
        loc = self.inputs[1].default_value
        return f'''
            float f_{self.index}(vec3 p){{
                return length(p-vec3({loc[0]},{loc[1]},{loc[2]}))-({self.inputs[0].default_value});
            }}
            '''

    def gen_glsl(self, ref_stack):
        me = self.index
        return '', f'''
            float d_{me}_{self.ref_num}=f_{me}(p_{me}_{self.ref_num});
        '''

    def gen_taichi_func(self):
        me = self.coll_index
        m = self.name
        return f'''
@ti.func
def f_{me}(p):
    return (p-ti.Vector([para[{self.coll_para_idx + 1}], para[{self.coll_para_idx + 2}], para[{self.coll_para_idx + 3}]])).norm() - para[{self.coll_para_idx}]

@ti.func
def update_p_by_collision(self, vi):
    rel_p = p - ti.Vector([para[{self.coll_para_idx + 1}], para[{self.coll_para_idx + 2}], para[{self.coll_para_idx + 3}]])
    rel_p_norm = rel_p.norm()
    sdf = rel_p.norm() - para[{self.coll_para_idx}]
    if sdf < 0:
        self.p[vi] += - sdf / rel_p_norm * rel_p
'''

    def gen_taichi(self, ref_stack):
        me = self.coll_index

        return '', f'''
    d_{me}_{self.coll_ref_num} = f_{me}(p_{me}_{self.coll_ref_num})
'''
