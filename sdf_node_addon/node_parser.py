import bpy


class NodeList(object):

    tree = None
    coll_tree = None

    def __init__(self):
        self.reset_display_nodes()

    def reset_display_nodes(self):
        self.node_list = []
        self.ref_stacks = []
        self.glsl_func_list = []
        self.glsl_p_list = []
        self.glsl_d_list = []
        self.glsl_func_text = ''
        self.glsl_sdf_text = ''

    def reset_collision_nodes(self):
        self.coll_node_list = []
        self.coll_ref_stacks = []
        self.taichi_func_list = []
        self.taichi_p_list = []
        self.taichi_d_list = []
        self.taichi_func_text = ''
        self.taichi_sdf_text = ''

    def gen_glsl_list(self, node):
        glsl = node.gen_glsl(self.ref_stacks)
        self.glsl_p_list.append(glsl[0])
        self.glsl_d_list.append(glsl[1])

    def gen_taichi_list(self, node):
        taichi_codes = node.gen_taichi(self.coll_ref_stacks)
        self.taichi_p_list.append(taichi_codes[0])
        self.taichi_d_list.append(taichi_codes[1])

    def gen_node_info(self, node_in):
        """
        index: -3: ignored, -1: unvisited
        """
        for node in self.tree.nodes:
            if node.index > -2:
                node.index = -1
                node.ref_num = 0
        self.followLinks(node_in, self.gen_glsl_list)

    def gen_coll_node_info(self, node_in):
        """
        index: -3: ignored, -1: unvisited
        """
        for node in self.coll_tree.nodes:
            if node.coll_index > -2:
                node.coll_index = -1
                node.coll_ref_num = 0
        self.collision_follow_links(node_in, self.gen_taichi_list)

    def gen_node_list(self, node_in):
        self.reset_display_nodes()
        self.tree = bpy.context.space_data.edit_tree
        self.gen_node_info(node_in)
        if self.node_list:
            num = len(self.node_list) - 1
            ref_n = self.node_list[num].ref_num

            for node in self.node_list:
                self.glsl_func_list.append(node.gen_glsl_func())
            self.glsl_p_list.reverse()

            self.glsl_sdf_text = f'''
            vec3 p_{num}_{ref_n} = p;
            ''' + ''.join(self.glsl_p_list) + ''.join(self.glsl_d_list) + f'''
            return d_{num}_{ref_n};
            '''
            self.glsl_func_text = ''.join(self.glsl_func_list)
            # inspect.cleandoc(self.glsl_sdf_text)

        else:
            self.glsl_sdf_text = 'return 2 * MAX_DIST;'

    def gen_collision_node_list(self, node_in):
        self.reset_collision_nodes()
        self.coll_tree = bpy.context.scene.sdf_physics.c_sdf
        self.gen_coll_node_info(node_in)
        if self.coll_node_list:
            coll_num = len(self.coll_node_list) - 1
            coll_ref_n = self.coll_node_list[coll_num].coll_ref_num

            para_idx = 0
            for node in self.coll_node_list:
                self.taichi_func_list.append(node.gen_taichi_func())
                node.coll_para_idx = para_idx
                para_idx += node.para_num

            self.taichi_p_list.reverse()

            self.taichi_sdf_text = f'''
    p_{coll_num}_{coll_ref_n} = p
            ''' + ''.join(self.taichi_p_list) + ''.join(self.taichi_d_list) + f'''
    return d_{coll_num}_{coll_ref_n}
            '''
            self.taichi_func_text = ''.join(self.taichi_func_list)
            # inspect.cleandoc(self.glsl_sdf_text)

        else:
            self.taichi_sdf_text = '''
    return 1e19'''

        

    def update_glsl_func(self, node):
        if self.node_list:
            self.glsl_func_list[node.index] = node.gen_glsl_func()
            self.glsl_func_text = ''.join(self.glsl_func_list)
            # inspect.cleandoc(self.glsl_sdf_text)

    def followLinks(self, node_in, operation):

        for n_inputs in node_in.inputs:
            for node_link in n_inputs.links:
                to_name = node_link.to_socket.bl_idname
                if node_link.from_socket.bl_idname == to_name:
                    # for all input nodes
                    node = node_link.from_node
                    if node.index > -2:
                        self.followLinks(node, operation)

                        if node.index < 0:
                            node.index = len(self.node_list)
                            self.node_list.append(node)
                            self.ref_stacks.append([0])
                        else:
                            node.ref_num += 1
                            self.ref_stacks[node.index].append(node.ref_num)

                        # print(node.name, ':', node.index, node.ref_num)
                        operation(node)
    
    def collision_follow_links(self, node_in, operation):
        for n_inputs in node_in.inputs:
            for node_link in n_inputs.links:
                to_name = node_link.to_socket.bl_idname
                if node_link.from_socket.bl_idname == to_name:
                    # for all input nodes
                    node = node_link.from_node
                    if node.coll_index > -2:
                        self.collision_follow_links(node, operation)

                        if node.coll_index < 0:
                            node.coll_index = len(self.coll_node_list)
                            self.coll_node_list.append(node)
                            self.coll_ref_stacks.append([0])
                        else:
                            node.coll_ref_num += 1
                            self.coll_ref_stacks[node.coll_index].append(node.coll_ref_num)

                        # print(node.name, ':', node.index, node.ref_num)
                        operation(node)
