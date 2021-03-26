import bpy


class NodeList(object):

    tree = None

    def __init__(self):
        self.reset()

    def reset(self):
        self.node_list = []
        self.ref_stacks = []
        self.glsl_func_list = []
        self.glsl_p_list = []
        self.glsl_d_list = []
        self.glsl_func_text = ''
        self.glsl_sdf_text = ''

    def gen_glsl_list(self, node):
        glsl = node.gen_glsl(self.ref_stacks)
        self.glsl_p_list.append(glsl[0])
        self.glsl_d_list.append(glsl[1])

    def gen_node_info(self, node_in):
        """
        index: -3: ignored, -1: unvisited
        """
        for node in self.tree.nodes:
            if node.index > -2:
                node.index = -1
                node.ref_num = 0
        self.followLinks(node_in, self.gen_glsl_list)

    def gen_node_list(self, node_in):
        self.reset()
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
