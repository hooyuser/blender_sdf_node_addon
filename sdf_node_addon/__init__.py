# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import nodeitems_utils

import os
import atexit

import taichi as ti

from . import auto_load
from .redrawViewport import Draw
from .node_status import SdfNodeProps
from .physics.physics_status import SdfPhyProps
from .physics.PBD_stretch_bend import temp

bl_info = {
    "name": "sdf node",
    "author": "DerivedCat",
    "description": "",
    "blender": (2, 90, 0),
    "version": (0, 0, 2),
    "location": "",
    "warning": "",
    "category": "Generic"
}


class CustomNodeCategory(nodeitems_utils.NodeCategory):
    # define the classmethod that tells blender which node tree
    #   the categories made with this class belong to (is visible to)
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'SDFNodeTree'


node_categories = [
    # NOTE: did not find documentation other then template script for it
    # esentially:
    #   we instantiate a new 'nodeitems_utils.NodeCategory' class, that
    #   has been extended with a poll method that makes sure that the
    #   category and node only shows up in the desired node tree
    # The first argument is a string with its id we will use to access it by
    # the second argument is the name displayed to the user
    # the third argument is a list of (items) nodes that are under
    #   that category, the list contains instances 'nodeitems_utils.NodeItem'
    CustomNodeCategory(
        "PRIMITIVES_NODES",
        "Primitives",
        items=[
            # the nodes (items) in this category are instantiated in this list
            #   with the 'nodeitems_utils.NodeItem' class, which can have
            #   additional settings
            # the first argument is the node class idname we want to add
            # then there can be keyword arguments like label
            # another argument can be a 'settings' keyword argument
            #   that takes a dictionary that can override default values of all
            #   properties
            #   NOTE: use 'repr()' to convert the value to string IMPORTANT
            nodeitems_utils.NodeItem("SphereSDF", label="Sphere"),
            nodeitems_utils.NodeItem("BoxSDF", label="Box"),
            nodeitems_utils.NodeItem("PlaneSDF", label="Plane"),
            nodeitems_utils.NodeItem("TorusSDF", label="Torus"),
            nodeitems_utils.NodeItem("CylinderSDF", label="Cylinder"),
            nodeitems_utils.NodeItem("ConeSDF", label="Cone")
        ]),
    CustomNodeCategory("OPERATION_NODES",
                       "Operation",
                       items=[
                           nodeitems_utils.NodeItem("Transform",
                                                    label="Transform"),
                           nodeitems_utils.NodeItem("Round", label="Round"),
                           nodeitems_utils.NodeItem("Solidify",
                                                    label="Solidify"),
                           nodeitems_utils.NodeItem("Array", label="Array"),
                           nodeitems_utils.NodeItem("Mirror", label="Mirror"),
                           nodeitems_utils.NodeItem("ClippedMirror",
                                                    label="Clipped Mirror"),
                           nodeitems_utils.NodeItem("Elongate",
                                                    label="Elongate"),
                           nodeitems_utils.NodeItem("Bend", label="Bend"),
                           nodeitems_utils.NodeItem("Twist", label="Twist"),
                       ]),
    CustomNodeCategory("CONSTRUCTION_NODES",
                       "Construction",
                       items=[
                           nodeitems_utils.NodeItem("Bool", label="Bool"),
                           nodeitems_utils.NodeItem("SmoothBool",
                                                    label="Smooth Bool"),
                           nodeitems_utils.NodeItem("Blend", label="Blend"),
                       ]),
    CustomNodeCategory("DISPLACEMENT_NODES",
                       "Displacement",
                       items=[
                           nodeitems_utils.NodeItem("SimplexNoise",
                                                    label="Simplex Noise"),
                           nodeitems_utils.NodeItem("FbmNoise",
                                                    label="FBM Noise"),
                           nodeitems_utils.NodeItem("WhiteNoise",
                                                    label="White Noise"),
                       ]),
    CustomNodeCategory("INPUT_NODES",
                       "Input",
                       items=[
                           nodeitems_utils.NodeItem("FloatInput",
                                                    label="Float"),
                           nodeitems_utils.NodeItem("IntegerInput",
                                                    label="Integer"),
                           nodeitems_utils.NodeItem("ObjectInfo",
                                                    label="Object Info"),
                       ]),
    CustomNodeCategory("OUTPUT_NODES",
                       "Output",
                       items=[
                           nodeitems_utils.NodeItem("Viewer", label="Viewer"),
                       ]),
    CustomNodeCategory("MATH_NODES",
                       "Math",
                       items=[
                           nodeitems_utils.NodeItem("FloatMath",
                                                    label="Float Math"),
                       ]),
    # CustomNodeCategory(
    #     "MISC_NODES",
    #     "Misc",
    #     items=[
    #         # the nodes (items) in this category are instantiated in this list
    #         #   with the 'nodeitems_utils.NodeItem' class, which can have
    #         #   additional settings
    #         # the first argument is the node class idname we want to add
    #         # then there can be keyword arguments like label
    #         # another argument can be a 'settings' keyword argument
    #         #   that takes a dictionary that can override default values of all
    #         #   properties
    #         #   NOTE: use 'repr()' to convert the value to string IMPORTANT
    #         nodeitems_utils.NodeItem("Add",
    #                                  label="Add",
    #                                  settings={"intProp": repr(1.0)}),
    #         # minimalistic node addition is like this
    #         # nodeitems_utils.NodeItem("CustomSimpleInputNode"),
    #     ]),
]

auto_load.init()


def register():
    auto_load.register()
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)

    bpy.types.Scene.sdf_physics = bpy.props.PointerProperty(type=SdfPhyProps)
    bpy.types.Scene.sdf_node_data = bpy.props.PointerProperty(
        type=SdfNodeProps)


def unregister():

    

    Draw.refreshViewport(False)

    auto_load.unregister()
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")

    del bpy.types.Scene.sdf_physics
    try:
        os.remove(temp.name)
    except FileNotFoundError:
        print(temp.name + ' not found!')


def cleanup_temp():
    try:
        os.remove(temp.name)
    except FileNotFoundError:
        print(temp.name + ' not found!')


atexit.register(cleanup_temp)

if __name__ == '__main__':
    register()
