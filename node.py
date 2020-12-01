# the little less documented way of adding a custom node tree
#   and populate it with nodes of varying types of I/O
#   sockets that work together, discombobulated

# first we import the blender API
import bpy
import nodeitems_utils


# then we create the UI space, the node tree as it is called
#   but in actualy fact this is similar to a UI panel/menu
#   and mostly handled in the background in terms of creation
# so let's define out custom node tree, inheriting from its base type
class CustomNodeTree(bpy.types.NodeTree):
    # the docstring here is used to generate documentation but
    #   also used to display a description to the user
    '''A custom node tree type'''
    # then we can give it a custom id to access it, if not given
    #   it will use the classname by default
    bl_idname = 'CustomNodeTree'
    # the label is the name that will be displayed to the user
    bl_label = 'Custom Node Tree'
    # the icon that will be displayed in the UI
    # NOTE: check the blender dev plugins to see icons in text editor
    bl_icon = 'BLENDER'


# that is all we needed to make a nodetree
# first for convenience we make a class from which all our nodes
#   will inherit from, saving us some typing
class CustomNode(bpy.types.Node):
    # this line makes the node visible only to the 'CustomNodeTree'
    #   node tree, essentially checking context
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CustomNodeTree'


# now we start making a simple input node that uses builtin
#   blender properties, this is the simplest node
# we define the node class that inherits from its mixin class
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

    # this method lets you design how the node properties
    #   are drawn on the side panel (to the right)
    #   if it is not defined, draw_buttons will be used instead
    # def draw_buttons_ext(self, context, layout):

    # OPTIONAL
    # we can use this function to dynamically define the label of
    #   the node, however defining the bl_label explicitly overrides it
    # def draw_label(self):
    #   return "this label is shown"


# now to be able to see the nodes in the add node menu AND see it on the
#   tool shelf (left panel) we need to define node categories and then
#   register them, the rest is handled automagickally by blender
# so first we import the utilities used for handling node categories


# now we can make our own category using the NodeCategory baseclass
#   as before we first make a mixin class to save space
class CustomNodeCategory(nodeitems_utils.NodeCategory):
    # define the classmethod that tells blender which node tree
    #   the categories made with this class belong to (is visible to)
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CustomNodeTree'


# make a list of node categories for registration
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
        "CUSTOMINPUTNODES",
        "Custom Input Nodes",
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
            nodeitems_utils.NodeItem("CustomSimpleInputNode"),
        ]),
]

# finally we register our classes so we can install as plugin
# to that end we create a list of classes to be loaded and unloaded
classes = (
    CustomNodeTree,
    CustomSimpleInputNode,
)


# for loading we define the registering of all defined classes
def register():
    # we register all our classes into blender
    for cls in classes:
        bpy.utils.register_class(cls)
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
    for cls in classes:
        bpy.utils.unregister_class(cls)


# finally we make it runnable in the text editor for quick testing
if __name__ == '__main__':
    # during test running there is a bug where registering or adding
    #   references to certain groups and categories cannot override
    #   existing ones, here is a workaround
    # we enter a try..finally block
    try:
        # first try unregistering the existing category
        # WARNING: ALWAYS triple check that you unload the correct
        #   things in this block, as it will not raise errors
        nodeitems_utils.unregister_node_categories("CUSTOM_NODES")
    finally:
        # finally, wether it suceeded or not, we can now register it again
        #   this essentially reloads existing/register changes made
        #   and thanks to the nature of the finally block, is always run
        register()
