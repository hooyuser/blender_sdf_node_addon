import bpy

from ...base_types.base_node import CustomNode


class CustomSimpleInputNode(bpy.types.Node, CustomNode):
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
        self.inputs.new("CustomNodeSocket", "Custom in")

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