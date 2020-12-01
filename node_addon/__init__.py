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
import redrawViewport

bl_info = {
    "name": "sdf node",
    "author": "DerivedCat",
    "description": "",
    "blender": (2, 90, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}


class CustomNodeTree(bpy.types.NodeTree):
    # the docstring here is used to generate documentation but
    #   also used to display a description to the user
    '''A custom node tree type'''
    # then we can give it a custom id to access it, if not given
    #   it will use the classname by default
    bl_idname = 'CustomNodeTree'
    # the label is the name that will be displayed to the user
    bl_label = 'SDF Nodes'
    # the icon that will be displayed in the UI
    # NOTE: check the blender dev plugins to see icons in text editor
    bl_icon = 'BLENDER'


class CustomNode(bpy.types.Node):
    # this line makes the node visible only to the 'CustomNodeTree'
    #   node tree, essentially checking context
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CustomNodeTree'


class CustomSimpleInputNode(CustomNode):
    # we can add a docstring that will be interpreted as description
    '''A simple input node'''
    # optionally we define an id that we can reference the node by
    bl_idname = 'Add'
    # we add a label that the node will show the user as its name
    bl_label = 'Add'
    # we can also add an icon to it
    bl_icon = 'PLUS'

    # we can add properties here that the node uses locally
    # NOTE: does not get drawn automatically
    intProp = bpy.props.IntProperty()

    # init function that is automagickally is called when the
    #   node is instantiated into the treem setup sockets here
    #   for both inputs and outputs
    def init(self, context):
        # makes a new output socket of type 'NodeSocketInt' with the
        #   label 'output' on it
        # NOTE: no elements will be drawn for output sockets
        self.outputs.new('NodeSocketInt', "output")

        self.inputs.new('NodeSocketInt', "input1")
        self.inputs.new('NodeSocketInt', "input2")

    # copy function is ran to initialize a copied node from
    #   an existing one
    def copy(self, node):
        print("copied node", node)

    # free function is called when an existing node is deleted
    def free(self):
        print("Node removed", self)

    # draw method for drawing node UI just like any other
    # NOTE: input sockets are drawn by their respective methods
    #   but output ones DO NOT for some reason, do it manually
    #   and connect the drawn value to the output socket
    def draw_buttons(self, context, layout):
        # create a slider for int values
        layout.prop(self, 'intProp')


class SphereSDFNode(CustomNode):
    '''A simple input node'''

    bl_idname = 'SphereSDF'
    bl_label = 'Sphere SDF'
    bl_icon = 'PLUS'

    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Radius")
        self.inputs[0].default_value = 1

        self.inputs.new('NodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")


class BoxSDFNode(CustomNode):
    '''A simple input node'''

    bl_idname = 'BoxSDF'
    bl_label = 'Box SDF'
    bl_icon = 'PLUS'

    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Length")
        self.inputs[0].default_value = 1

        self.inputs.new('NodeSocketFloat', "Width")
        self.inputs[1].default_value = 1

        self.inputs.new('NodeSocketFloat', "Height")
        self.inputs[2].default_value = 1

        self.inputs.new('NodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")


operationItems = [("UNION", "Union", "Union", "", 0),
                  ("SUBTRACT", "Subtract", "Subtract", "", 1)]

operationLabels = {"UNION": "Union", "SUBTRACT": "Subtract"}


class BoolNode(CustomNode):
    '''A simple input node'''

    bl_idname = 'Bool'
    bl_label = 'Bool'
    bl_icon = 'PLUS'

    operation = bpy.props.EnumProperty(name="Operation",
                                       default="UNION",
                                       items=operationItems)

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="")

    def draw_label(self):
        return operationLabels[self.operation]

    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Distance 1")
        self.inputs[0].hide_value = True

        self.inputs.new('NodeSocketFloat', "Distance 2")
        self.inputs[1].hide_value = True

        self.outputs.new('NodeSocketFloat', "Distance")


class ViewerNode(CustomNode):
    '''A simple input node'''

    bl_idname = 'Viewer'
    bl_label = 'Viewer'
    bl_icon = 'PLUS'

    def redraw3DViewport(self, context):
        redrawViewport.Draw.refreshViewport(self.enabled)

    enabled = bpy.props.BoolProperty(name="Enabled",
                                     default=False,
                                     update=redraw3DViewport)

    def draw_buttons(self, context, layout):
        layout.prop(self, "enabled", text="Show SDF")

    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Distance")
        self.inputs[0].hide_value = True


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
        ]),
    CustomNodeCategory("OPERATIONS_NODES",
                       "Operations",
                       items=[
                           nodeitems_utils.NodeItem("Bool", label="Bool"),
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

classes = (CustomNodeTree, CustomSimpleInputNode, SphereSDFNode, BoxSDFNode,
           BoolNode, ViewerNode)


# for loading we define the registering of all defined classes
def register():
    # we register all our classes into blender
    for cl in classes:
        bpy.utils.register_class(cl)
    # we register the node categories with the node tree
    # the first argument is a string that is the idname for this collection
    #   of categories
    # the second is the actual list of node categories to be registered under
    #   this name
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)


# for unloading we define the unregistering of all defined classes
def unregister():
    # we unregister our node categories first
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")
    # then we unregister all classes from the blender
    for cl in classes:
        bpy.utils.unregister_class(cl)


if __name__ == '__main__':
    register()
