import bpy

from ..redrawViewport import Draw


class CustomNodeSocket(bpy.types.NodeSocket):
    bl_idname = "CustomNodeSocket"
    bl_label = "Custom Node Socket"

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
