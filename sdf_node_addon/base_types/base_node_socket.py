import bpy

from ..redrawViewport import Draw
from ..physics.PBD_stretch_bend import TiClothSimulation


class BaseNodeSocket(object):
    def default_value_callback(self, context):
        Draw.update_callback(update_node=self.node)
        TiClothSimulation.sdf_para_changed = True


#     socket_types = [("FLOAT", "Float", "Where your feet are"),
#                     ("INT", "Int", "Where your head should be"),
#                     ("SDF", "SDF", "Not right"),
#                     ("FLOAT_VEC", "Float_Vec", "Not left"),
#                     ("UNDEFINED", "Undefined", "N")]

#     mySocketType: bpy.props.EnumProperty(name="SocketType",
#                                          description="Just an example",
#                                          items=socket_types,
#                                          default='UNDEFINED')


class CustomNodeSocket(bpy.types.NodeSocket):
    bl_idname = "CustomNodeSocket"
    bl_label = "Custom Node Socket"

    # Enum items list
    my_items = [("DOWN", "Down", "Where your feet are"),
                ("UP", "Up", "Where your head should be"),
                ("LEFT", "Left", "Not right"), ("RIGHT", "Right", "Not left")]

    myEnumProperty: bpy.props.EnumProperty(name="Direction",
                                           description="Just an example",
                                           items=my_items,
                                           default='UP')

    myIntProp: bpy.props.IntProperty()

    translation: bpy.props.FloatVectorProperty(subtype='TRANSLATION')

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=self.name)
        else:
            col = layout.column()
            col.prop(self, "translation", text=self.name)

    def draw_color(self, context, node):
        return (1, 1, 1, 1)


class SdfNodeSocketPositiveInt(bpy.types.NodeSocket, BaseNodeSocket):
    bl_idname = "SdfNodeSocketPositiveInt"
    bl_label = "SDF Node Socket Positive Int"

    default_value: bpy.props.IntProperty(
        soft_min=0, update=BaseNodeSocket.default_value_callback)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, "default_value", text=self.name)

    def draw_color(self, context, node):
        return (0.7, 0.55, 0.2, 1)


class SdfNodeSocketFloat(bpy.types.NodeSocket, BaseNodeSocket):
    bl_idname = "SdfNodeSocketFloat"
    bl_label = "SDF Node Socket Float"

    default_value: bpy.props.FloatProperty(
        update=BaseNodeSocket.default_value_callback)
    my_type: bpy.props.StringProperty(name='mySocketType', default='FLOAT')

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        # self.my_string = 'FLOAT'
        if self.is_output or self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, "default_value", text=self.name)

    def draw_color(self, context, node):
        return (0.4, 0.5, 0.6, 1)


class SdfNodeSocketPositiveFloat(bpy.types.NodeSocket, BaseNodeSocket):
    bl_idname = "SdfNodeSocketPositiveFloat"
    bl_label = "SDF Node Socket Positive Float"

    default_value: bpy.props.FloatProperty(
        soft_min=0.0, update=BaseNodeSocket.default_value_callback)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, "default_value", text=self.name)

    def draw_color(self, context, node):
        return (0.643, 0.788, 0.824, 1)


class SdfNodeSocketFloatVector(bpy.types.NodeSocket, BaseNodeSocket):

    bl_idname = "SdfNodeSocketFloatVector"
    bl_label = "SDF Node Socket Float Vector"

    default_value: bpy.props.FloatVectorProperty(
        update=BaseNodeSocket.default_value_callback)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            col = layout.column()
            col.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        return (0.3, 0.4, 0.7, 1)


class SdfNodeSocketVectorTranslation(bpy.types.NodeSocket, BaseNodeSocket):

    bl_idname = "SdfNodeSocketVectorTranslation"
    bl_label = "SDF Node Socket Vector Translation"

    default_value: bpy.props.FloatVectorProperty(
        subtype='TRANSLATION', update=BaseNodeSocket.default_value_callback)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            col = layout.column()
            col.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        return (0.4, 0.4, 0.8, 1)


class SdfNodeSocketEuler(bpy.types.NodeSocket, BaseNodeSocket):

    bl_idname = "SdfNodeSocketEuler"
    bl_label = "SDF Node Socket Euler"

    default_value: bpy.props.FloatVectorProperty(
        default=[0, 0, 0],
        update=BaseNodeSocket.default_value_callback,
        subtype="EULER")

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            col = layout.column()
            col.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        return (0.3, 0.7, 0.45, 1)


class SdfNodeSocketSd(bpy.types.NodeSocket):
    bl_idname = "SdfNodeSocketSd"
    bl_label = "SdfNodeSocketSd"

    def draw(self, context, layout, node, text):
        layout.label(text='SDF')

    def draw_color(self, context, node):
        return (0.5, 0.5, 0.5, 1)


class SdfNodeSocketOperation(bpy.types.NodeSocket, BaseNodeSocket):
    bl_idname = "SdfNodeSocketOperation"
    bl_label = "SDF Node Socket Operation"

    default_value: bpy.props.FloatVectorProperty(
        update=BaseNodeSocket.default_value_callback)

    def draw(self, context, layout, node, text):
        layout.label(text='Operation')

    def draw_color(self, context, node):
        return (0.8, 0.3, 0.023, 1)
