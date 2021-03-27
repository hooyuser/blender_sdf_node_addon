import bpy
import importlib
import tempfile

from sys import path
import pathlib

from ..node_parser import NodeList

coll_node_list = NodeList()

taichi_sdf_func_header = '''
@ti.func
def ti_sdf(p):'''

temp = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
temp.close()
temp_path = pathlib.Path(temp.name)
path.append(str(temp_path.parent))
sdf_mod = importlib.import_module(temp_path.stem)


def gen_sdf_taichi(c_sdf):
    if bpy.context.scene.sdf_physics.c_sdf:
        coll_node = bpy.context.scene.sdf_node_data.active_collider
        if coll_node:
            coll_node_list.gen_collision_node_list(coll_node)
            taichi_sdf_codes = coll_node_list.taichi_func_text + \
                taichi_sdf_func_header + coll_node_list.taichi_sdf_text
            print(taichi_sdf_codes)
            with open(temp.name, "w") as f:
                f.write(taichi_sdf_codes)
            importlib.reload(sdf_mod)
