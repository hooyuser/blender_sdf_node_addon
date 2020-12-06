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

import nodeitems_utils

from . import auto_load
from .redrawViewport import Draw

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
        return context.space_data.tree_type == 'CustomNodeTree'


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
            nodeitems_utils.NodeItem("TorusSDF", label="Torus"),
            nodeitems_utils.NodeItem("ConeSDF", label="Cone")
        ]),
    CustomNodeCategory("OPERATIONS_NODES",
                       "Operations",
                       items=[
                           nodeitems_utils.NodeItem("Bool", label="Bool"),
                           nodeitems_utils.NodeItem("SmoothBool",
                                                    label="Smooth Bool"),
                           nodeitems_utils.NodeItem("Round", label="Round"),
                           nodeitems_utils.NodeItem("Onion", label="Onion"),
                           nodeitems_utils.NodeItem("Operate", label="Operate"),
                           nodeitems_utils.NodeItem("Mirror", label="Mirror"),
                       ]),
    CustomNodeCategory("OUTPUT_NODES",
                       "Output",
                       items=[
                           nodeitems_utils.NodeItem("Viewer", label="Viewer"),
                       ]),
    CustomNodeCategory(
        "MISC_NODES",
        "Misc",
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
            nodeitems_utils.NodeItem("Add",
                                     label="Add",
                                     settings={"intProp": repr(1.0)}),
            # minimalistic node addition is like this
            # nodeitems_utils.NodeItem("CustomSimpleInputNode"),
        ]),
]

auto_load.init()


def register():
    auto_load.register()
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)


def unregister():
    Draw.refreshViewport(False)
    auto_load.unregister()
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")


if __name__ == '__main__':
    register()