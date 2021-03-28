import bpy

from ...base_types.base_node import CustomNode

vec_category = ['SdfNodeSocketVectorTranslation', 'SdfNodeSocketFloatVector']


class ObjectInfoNode(bpy.types.Node, CustomNode):
    '''An object information node'''

    bl_idname = 'ObjectInfo'
    bl_label = 'Object Info'
    bl_icon = 'ITALIC'

    def update_obj(self, context):
        def update_obj_loc(scene):
            if getattr(self, 'obj', False):
                for link in self.outputs[0].links:
                    link.to_socket.default_value = getattr(
                        self, 'obj').location.copy()

        if getattr(self, 'obj', False):
            try:
                bpy.app.handlers.frame_change_post.remove(update_obj_loc)
                bpy.app.handlers.depsgraph_update_pre.remove(update_obj_loc)
            except ValueError:
                print(
                    f'The handler of the object {self.obj.name} does not exist!'
                )
            bpy.app.handlers.frame_change_post.append(update_obj_loc)
            bpy.app.handlers.depsgraph_update_pre.append(update_obj_loc)

    obj: bpy.props.PointerProperty(name="obj",
                                   type=bpy.types.Object,
                                   description="Object",
                                   update=update_obj)

    def init(self, context):
        self.index = -3
        self.coll_index = -3
        self.outputs.new(type='SdfNodeSocketVectorTranslation',
                         name="Location")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'obj', text='Object')

    def update(self):
        if self.outputs[0].links:
            tree = self.id_data
            for link in self.outputs[0].links:
                if link.to_socket.bl_idname in vec_category:
                    link.to_socket.default_value = self.obj.location.copy()
                else:
                    tree.links.remove(link)
