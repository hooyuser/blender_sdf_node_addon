import bpy
from ...base_types.base_node import CustomNode


class OperateNode(bpy.types.Node, CustomNode):
    '''Operate node'''

    bl_idname = 'Operate'
    bl_label = 'Operate'
    bl_icon = 'MODIFIER'

    def init(self, context):
        self.inputs.new('NodeSocketFloat', "SDF")
        self.inputs[0].hide_value = True

        self.inputs.new('SdfNodeSocketOperation', "Operation")

        self.outputs.new('NodeSocketFloat', "SDF")

    def gen_glsl(self):

        if self.mirror_axis[0]:
            glsl_code = '''
            float d;
            '''

        return glsl_code
