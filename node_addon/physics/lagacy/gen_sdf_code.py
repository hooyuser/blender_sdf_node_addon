# import bpy
# import importlib
# import tempfile

# from sys import path
# import pathlib

# from ..node_parser import NodeList

# coll_node_list = NodeList()

# sdf_func_ins_1 = '''
# import taichi as ti

# '''

# sdf_func_ins_2 = '''
# @ti.func
# def ti_sdf(p):'''

# temp = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
# temp.close()
# temp_path = pathlib.Path(temp.name)
# path.append(str(temp_path.parent))
# sdf_mod = importlib.import_module(temp_path.stem)

# def gen_sdf_taichi():
#     collision_tree = bpy.context.scene.sdf_physics.c_sdf
#     if collision_tree:
#         coll_node = bpy.context.scene.sdf_node_data.active_collider
#         if coll_node:
#             coll_node_list.gen_collision_node_list(
#                 collision_tree.nodes[coll_node])
#             taichi_sdf_codes = sdf_func_ins_1 + coll_node_list.taichi_func_text + \
#                 sdf_func_ins_2 + coll_node_list.taichi_sdf_text
#             print('**taichi_sdf_codes:\n' + taichi_sdf_codes)
#             with open(temp.name, "w") as f:
#                 f.write(taichi_sdf_codes)
#             importlib.reload(sdf_mod)
