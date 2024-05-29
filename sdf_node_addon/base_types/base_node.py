import bpy
from ..redrawViewport import Draw

from datetime import datetime

# from ..physics.gen_taichi_code import gen_sdf_taichi


class CustomNode(object):
    # this line makes the node visible only to the 'SDFNodeTree'
    #   node tree, essentially checking context
    bpy.types.Node.index = bpy.props.IntProperty()
    bpy.types.Node.coll_index = bpy.props.IntProperty()
    # index = -1: to be searched. index = -2: will not be searched

    bpy.types.Node.ref_num = bpy.props.IntProperty()
    bpy.types.Node.coll_ref_num = bpy.props.IntProperty()
    # ref_num actually equals the referencing number - 1

    bpy.types.Node.coll_para_idx = bpy.props.IntProperty()

    # the index of the first parameter of a node

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SDFNodeTree'

    def update(self):
        print(f'[{datetime.now().strftime("%H:%M:%S")}] Node Updated: {self.name}')
        if self.outputs:
            if hasattr(bpy.context.space_data, 'edit_tree'):
                tree = bpy.context.space_data.edit_tree
                if self.outputs[0].links:
                    for link in self.outputs[0].links:
                        to_node = link.to_node
                        if link.to_socket.bl_idname != 'SdfNodeSocketSdf':
                            tree.links.remove(link)
                            tree.links.new(self.outputs[0],
                                           to_node.inputs[-1]).is_valid = True
        Draw.update_callback()
        bpy.context.scene.sdf_node_data.material_nodes = '|'.join(
            [node.name for node in Draw.glsl_nodes.material_node_list])
        # gen_sdf_taichi()

    def free(self):
        print(f'[{datetime.now().strftime("%H:%M:%S")}] Node Removed: {self.name}')
        Draw.update_callback()
        if self in Draw.glsl_nodes.material_node_list:
            Draw.glsl_nodes.material_node_list.remove(self)
        bpy.context.scene.sdf_node_data.material_nodes = '|'.join(
            [node.name for node in Draw.glsl_nodes.material_node_list])
        # self.last_update = self

    def gen_glsl_uniform_helper(self):

        glsl_identifier = {"<class 'Vector'>": 'vec3',
                           "<class 'Color'>": 'vec3',
                           "<class 'float'>": 'float'}

        glsl_uniform_list = [
            f'''uniform {glsl_identifier[str(type(input.default_value))]} u_{self.index}_{input.name};\n'''
            for input in self.inputs
            if input.bl_idname != 'SdfNodeSocketSdf']

        def gen_glsl_uniform(self):
            return ''.join(glsl_uniform_list)

        return gen_glsl_uniform
