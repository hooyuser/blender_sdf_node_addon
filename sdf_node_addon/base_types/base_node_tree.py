import bpy


class SDFNodeTree(bpy.types.NodeTree):
    # the docstring here is used to generate documentation but
    #   also used to display a description to the user
    '''A custom node tree type'''
    # then we can give it a custom id to access it, if not given
    #   it will use the classname by default
    bl_idname = 'SDFNodeTree'
    # the label is the name that will be displayed to the user
    bl_label = 'SDF Nodes'
    # the icon that will be displayed in the UI
    # NOTE: check the blender dev plugins to see icons in text editor
    bl_icon = 'SCRIPTPLUGINS'
