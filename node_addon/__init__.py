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
import inspect

import bpy
import nodeitems_utils

from .redrawViewport import Draw
from .base_types.base_node import CustomNode
from .nodes.viewer.viewer import ViewerNode
from . import nodes
# from .addonStatus import Status

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

a = [globals()[x] for x in dir(nodes) if inspect.isclass(getattr(nodes, x))]


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


class CustomNodeSocket(bpy.types.NodeSocket):
    bl_idname = "CustomNodeSocket"
    bl_label = "Custom Node Socket"

    def my_update_callback(self, context):
        print('callback')

    # Enum items list
    my_items = [("DOWN", "Down", "Where your feet are"),
                ("UP", "Up", "Where your head should be"),
                ("LEFT", "Left", "Not right"), ("RIGHT", "Right", "Not left")]

    myEnumProperty = bpy.props.EnumProperty(name="Direction",
                                            description="Just an example",
                                            items=my_items,
                                            default='UP')

    myIntProp = bpy.props.IntProperty()

    translation = bpy.props.FloatVectorProperty(subtype='TRANSLATION')

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=self.name)
        else:
            col = layout.column()
            col.prop(self, "translation", text=self.name)

    def draw_color(self, context, node):
        return (1, 1, 1, 1)


# def update_callback():
#     for node in bpy.context.space_data.edit_tree.nodes:
#         if node.bl_idname == 'Viewer':
#             print('has Viewer')
#             if node.enabled:
#                 Draw.refreshViewport(False)
#                 Draw.refreshViewport(True)


class SdfNodeSocketFloat(bpy.types.NodeSocket):
    bl_idname = "SdfNodeSocketFloat"
    bl_label = "SDF Node Socket Float"

    def default_value_callback(self, context):
        Draw.update_callback()

    default_value = bpy.props.FloatProperty(subtype='UNSIGNED',
                                            min=0.0,
                                            update=default_value_callback)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, "default_value", text=self.name)

    def draw_color(self, context, node):
        return (0.443, 0.588, 0.624, 1)


class SdfNodeSocketVectorTranslation(bpy.types.NodeSocket):
    bl_idname = "SdfNodeSocketVectorTranslation"
    bl_label = "SDF Node Socket Vector Translation"

    def default_value_callback(self, context):
        Draw.update_callback()

    default_value = bpy.props.FloatVectorProperty(
        subtype='TRANSLATION', update=default_value_callback)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text='Location')
        else:
            col = layout.column()
            col.prop(self, "default_value", text='Location')

    def draw_color(self, context, node):
        return (0.2, 0.2, 0.8, 1)


# class CustomNode(bpy.types.Node):
#     # this line makes the node visible only to the 'CustomNodeTree'
#     #   node tree, essentially checking context
#     bpy.types.Node.index = bpy.props.IntProperty()

#     @classmethod
#     def poll(cls, ntree):
#         return ntree.bl_idname == 'CustomNodeTree'

#     def update(self):
#         Draw.update_callback()


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


class SphereSDFNode(CustomNode):
    '''A simple input node'''

    bl_idname = 'SphereSDF'
    bl_label = 'Sphere SDF'
    bl_icon = 'PLUS'

    def redraw(self):
        v = bpy.data.node_groups["NodeTree"].nodes.get("Viewer")
        if v:
            if v.enabled:
                Draw.refreshViewport(False)
                Draw.refreshViewport(True)

    def init(self, context):
        self.index = -1

        self.inputs.new('SdfNodeSocketFloat', "Radius")
        self.inputs[0].default_value = 1

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        loc = self.inputs[1].default_value
        glsl_code = '''
            float d_{}=length(p-vec3({},{},{}))-{};
        '''.format(self.index, loc[0], loc[1], loc[2],
                   self.inputs[0].default_value)

        return glsl_code


class BoxSDFNode(CustomNode):
    '''A simple input node'''

    bl_idname = 'BoxSDF'
    bl_label = 'Box SDF'
    bl_icon = 'PLUS'

    def init(self, context):

        self.inputs.new('SdfNodeSocketFloat', "Length")
        self.inputs[0].default_value = 1

        self.inputs.new('SdfNodeSocketFloat', "Width")
        self.inputs[1].default_value = 1

        self.inputs.new('SdfNodeSocketFloat', "Height")
        self.inputs[2].default_value = 1

        self.inputs.new('SdfNodeSocketVectorTranslation', "Location")

        self.outputs.new('NodeSocketFloat', "Distance")

    def gen_glsl(self):
        loc = self.inputs[3].default_value
        glsl_code = '''
            vec3 q_{} = abs(p - vec3({},{},{})) - vec3({},{},{});
            float d_{} = length(max(q_{},0.0)) +
                min(max(q_{}.x,max(q_{}.y,q_{}.z)),0.0);
        '''.format(self.index, loc[0], loc[1], loc[2],
                   self.inputs[0].default_value, self.inputs[1].default_value,
                   self.inputs[2].default_value, self.index, self.index,
                   self.index, self.index, self.index)

        return glsl_code


class BoolNode(CustomNode):
    '''A simple input node'''

    bl_idname = 'Bool'
    bl_label = 'Bool'
    bl_icon = 'PLUS'

    operationItems = [
        ("UNION", "Union", "Union", "", 0),
        ("INTERSECT", "Intersect", "Intersect", "", 1),
        ("SUBTRACT", "Subtract", "Subtract", "", 2),
    ]

    operationLabels = {
        "UNION": "Union",
        "INTERSECT": "Intersect",
        "SUBTRACT": "Subtract"
    }

    def update_prop(self, context):
        Draw.update_callback()

    operation = bpy.props.EnumProperty(name="Operation",
                                       default="UNION",
                                       items=operationItems,
                                       update=update_prop)

    def draw_buttons(self, context, layout):

        layout.prop(self, "operation", text="")

    def draw_label(self):
        return self.operationLabels[self.operation]

    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Distance 1")
        self.inputs[0].hide_value = True

        self.inputs.new('NodeSocketFloat', "Distance 2")
        self.inputs[1].hide_value = True

        self.outputs.new('SdfNodeSocketFloat', "Distance")

    def gen_glsl(self):
        input_0 = 'd_' + str(bpy.data.node_groups["NodeTree"].nodes[
            self.inputs[0].links[0].from_node.name].index
                             ) if self.inputs[0].links else '2.0 * MAX_DIST'
        input_1 = 'd_' + str(bpy.data.node_groups["NodeTree"].nodes[
            self.inputs[1].links[0].from_node.name].index
                             ) if self.inputs[1].links else '2.0 * MAX_DIST'

        if self.operation == "UNION":
            glsl_code = '''
            float d_{}=min({},{});
            '''.format(self.index, input_0, input_1)
        elif self.operation == "INTERSECT":
            glsl_code = '''
            float d_{}=max({},{});
            '''.format(self.index, input_0, input_1)
        else:
            glsl_code = '''
            float d_{}=max(-{},{});
            '''.format(self.index, input_0, input_1)

        return glsl_code


class SmoothBoolNode(CustomNode):
    '''A simple input node'''

    bl_idname = 'SmoothBool'
    bl_label = 'Smooth Bool'
    bl_icon = 'PLUS'

    operationItems = [
        ("S_UNION", "Smooth Union", "Smooth Union", "", 0),
        ("S_INTERSECT", "Smooth Intersect", "Smooth Intersect", "", 1),
        ("S_UBTRACT", "Smooth Subtract", "Smooth Subtract", "", 2)
    ]

    operationLabels = {
        "S_UNION": "Smooth Union",
        "S_INTERSECT": "Smooth Intersect",
        "S_SUBTRACT": "Smooth Subtract"
    }

    def update_prop(self, context):
        Draw.update_callback()

    operation = bpy.props.EnumProperty(name="Operation",
                                       default="S_UNION",
                                       items=operationItems,
                                       update=update_prop)

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="")

    def draw_label(self):
        return self.operationLabels[self.operation]

    def init(self, context):

        self.inputs.new('SdfNodeSocketFloat', "Smoothness")
        self.inputs[0].default_value = 0.25

        self.inputs.new('NodeSocketFloat', "Distance 1")
        self.inputs[1].hide_value = True

        self.inputs.new('NodeSocketFloat', "Distance 2")
        self.inputs[2].hide_value = True

        self.outputs.new('SdfNodeSocketFloat', "Distance")

    def gen_glsl(self):
        k = self.inputs[0].default_value
        input_1 = 'd_' + str(bpy.data.node_groups["NodeTree"].nodes[
            self.inputs[1].links[0].from_node.name].index
                             ) if self.inputs[1].links else '2.0 * MAX_DIST'
        input_2 = 'd_' + str(bpy.data.node_groups["NodeTree"].nodes[
            self.inputs[2].links[0].from_node.name].index
                             ) if self.inputs[2].links else '2.0 * MAX_DIST'

        if self.operation == "S_UNION":
            glsl_code = '''
            float h_{} = max({}-abs({}-{}),0.0);
            float d_{} = min({},{}) - h_{}*h_{}*0.25/{};
            '''.format(self.index, k, input_1, input_2, self.index, input_1,
                       input_2, self.index, self.index, k)
        elif self.operation == "S_INTERSECT":
            glsl_code = '''
            float h_{} = max({}-abs({}-{}),0.0);
            float d_{} = max({},{}) + h_{}*h_{}*0.25/{};
            '''.format(self.index, k, input_1, input_2, self.index, input_1,
                       input_2, self.index, self.index, k)
        else:
            glsl_code = '''
            float h_{} = max({}-abs(-{}-{}),0.0);
            float d_{} = max(-{},{}) + h_{}*h_{}*0.25/{};
            '''.format(self.index, k, input_1, input_2, self.index, input_1,
                       input_2, self.index, self.index, k)

        return glsl_code


# class ViewerNode(CustomNode):
#     '''A simple input node'''

#     bl_idname = 'Viewer'
#     bl_label = 'Viewer'
#     bl_icon = 'PLUS'

#     def redraw3DViewport(self, context):
#         Draw.refreshViewport(self.enabled)

#     enabled = bpy.props.BoolProperty(name="Enabled",
#                                      default=False,
#                                      update=redraw3DViewport)

#     def draw_buttons(self, context, layout):
#         layout.prop(self, "enabled", text="Show SDF")

#     # def update(self):
#     #     if self.inputs[0].links:
#     #         Draw.refreshViewport(False)
#     #         Draw.refreshViewport(True)

#     def init(self, context):
#         self.inputs.new('NodeSocketFloat', "Distance")
#         self.inputs[0].hide_value = True

#     def free(self):
#         Draw.refreshViewport(False)


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
                           nodeitems_utils.NodeItem("SmoothBool",
                                                    label="Smooth Bool")
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

classes = (CustomNodeSocket, CustomNodeTree, CustomSimpleInputNode,
           SdfNodeSocketFloat, SdfNodeSocketVectorTranslation, SphereSDFNode,
           BoxSDFNode, BoolNode, SmoothBoolNode, ViewerNode)


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
    # bpy.app.timers.register(Draw.every_second)
    # bpy.app.handlers.load_post.append(load_handler)


# for unloading we define the unregistering of all defined classes
def unregister():
    # we unregister our node categories first
    Draw.refreshViewport(False)
    # bpy.app.handlers.load_post.remove(load_handler)

    # then we unregister all classes from the blender
    for cl in classes:
        bpy.utils.unregister_class(cl)
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")


if __name__ == '__main__':
    register()
