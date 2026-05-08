bl_info = {
    "name": "Outliner Organizer",
    "author": "",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "Outliner > Right Click",
    "description": "Right-click in Outliner to create collections and move objects in one step",
    "category": "Interface",
}

import bpy
from bpy.types import Operator

# ── Internationalization ──────────────────────────────────────────────

TRANSLATIONS = {
    "zh_CN": {
        ("*", "New Collection for Selected"):
            "为所选项新建文件夹",
        ("*", "New Collection per Selected"):
            "为所选新建独立文件夹",
    },
}

# ── Operators ─────────────────────────────────────────────────────────

class OUTLINER_OT_new_collection_move(Operator):
    """Create a new collection named after the selection and move objects into it.
    Single object → new collection with same name.
    Multiple objects → one collection named after the right-clicked (active) object."""
    bl_idname = "outliner.new_collection_move"
    bl_label = "New Collection for Selected"
    bl_translation_context = "*"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return any(isinstance(id_data, bpy.types.Object) for id_data in context.selected_ids)

    def execute(self, context):
        objects = [
            id_data for id_data in context.selected_ids
            if isinstance(id_data, bpy.types.Object)
        ]
        if not objects:
            self.report({"WARNING"}, "No objects selected")
            return {"CANCELLED"}

        # Use active/right-clicked object name for multi, or the single object name
        if len(objects) == 1:
            col_name = objects[0].name
        else:
            col_name = context.id.name

        col = bpy.data.collections.new(col_name)
        context.scene.collection.children.link(col)

        for obj in objects:
            for existing_col in list(obj.users_collection):
                existing_col.objects.unlink(obj)
            col.objects.link(obj)

        count = len(objects)
        self.report({"INFO"}, f"Moved {count} object{'s' if count > 1 else ''} to '{col.name}'")
        return {"FINISHED"}


class OUTLINER_OT_new_collection_each(Operator):
    """Create a separate collection for each selected object, named after it.
    Single object → same as New Collection & Move.
    Multiple objects → one collection per object, each with the object's name."""
    bl_idname = "outliner.new_collection_each"
    bl_label = "New Collection per Selected"
    bl_translation_context = "*"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return any(isinstance(id_data, bpy.types.Object) for id_data in context.selected_ids)

    def execute(self, context):
        objects = [
            id_data for id_data in context.selected_ids
            if isinstance(id_data, bpy.types.Object)
        ]
        if not objects:
            self.report({"WARNING"}, "No objects selected")
            return {"CANCELLED"}

        count = 0
        for obj in objects:
            col = bpy.data.collections.new(obj.name)
            context.scene.collection.children.link(col)
            for existing_col in list(obj.users_collection):
                existing_col.objects.unlink(obj)
            col.objects.link(obj)
            count += 1

        self.report({"INFO"}, f"Moved {count} object{'s' if count > 1 else ''} to individual collections")
        return {"FINISHED"}


def draw_outliner_object_menu(self, context):
    layout = self.layout
    layout.operator("outliner.new_collection_move")
    layout.operator("outliner.new_collection_each")


classes = [
    OUTLINER_OT_new_collection_move,
    OUTLINER_OT_new_collection_each,
]


def register():
    bpy.app.translations.register(__name__, TRANSLATIONS)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.OUTLINER_MT_object.prepend(draw_outliner_object_menu)


def unregister():
    bpy.app.translations.unregister(__name__)
    bpy.types.OUTLINER_MT_object.remove(draw_outliner_object_menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
