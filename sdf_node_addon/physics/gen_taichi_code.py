# import bpy
# from ..node_parser import NodeList

# enable_analitical_grad = True
# coll_nodes = NodeList()



# def gen_sdf_taichi():
#     global enable_analitical_grad
#     sdf_phy = bpy.context.scene.sdf_physics
#     collision_tree = sdf_phy.c_sdf
#     if collision_tree:
#         coll_node = bpy.context.scene.sdf_node_data.active_collider
#         if coll_node:
#             coll_nodes.gen_collision_node_list(
#                 collision_tree.nodes[coll_node])
#             taichi_sdf_codes = f'''
# import bpy
# import taichi as ti
# ''' + coll_nodes.taichi_func_text + '''
# @ti.func
# def ti_sdf(p):
# ''' + coll_nodes.taichi_sdf_text

#             print('**taichi_sdf_codes:\n' + taichi_sdf_codes)
#             with open(temp.name, "w") as f:
#                 f.write(taichi_sdf_codes)
#             importlib.reload(sdf_mod)
#             if len(coll_nodes.coll_node_list
#                    ) == 1 and bpy.context.scene.sdf_physics.analytical_grad:
#                 enable_analitical_grad = True
#             else:
#                 enable_analitical_grad = False
