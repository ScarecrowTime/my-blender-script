bl_info = {
    "name": "Apply Specific Modifier",
    "author": "Scarecrow_Time",
    "version": (2, 0),
    "blender": (5, 2, 2),
    "location": "View3D > N-Panel > Apply Mod",
    "description": "Применяет модификатор с заданным именем к выбранным объектам",
    "category": "Object",
}
import bpy # Подключаем модуль Blender Python API

# Настройка: имя модификатора вынесено в удобное поле аддона
class MyModifierSettings(bpy.types.PropertyGroup):
    modifier_name: bpy.props.StringProperty(name="Имя модификатора",
        description="Укажите точное имя модификатора для применения (чувствительно к регистру!)",
        default="")

# ОПЕРАТОР: Здесь живёт вся логика скрипта
class OBJECT_OT_apply_specific_modifier(bpy.types.Operator):
    bl_idname = "object.apply_specific_modifier"
    bl_label = "Применить модификатор"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Получаем имя модификатора из поля ввода на панели
        modifier_name_to_apply = context.scene.my_mod_settings.modifier_name
        # Сохраняем исходный активный объект, чтобы не сбить выделение
        original_active = context.view_layer.objects.active

        # Списки для хранения результатов(сделаны локальными для оператора)
        self.success_objects = []
        self.failed_objects = []
        self.not_found_objects = []

        for obj in context.selected_objects:
            # Проверяем, является ли объект мешем
            if obj.type == 'MESH':
                # проверяем, есть ли нужный модификатор
                if modifier_name_to_apply in obj.modifiers:
                    # Делаем текущий объект активным для Blender
                    context.view_layer.objects.active = obj
                    # Применяем модификатор
                    try:
                        bpy.ops.object.modifier_apply(modifier=modifier_name_to_apply)
                        print(f"Modifier successfully applied to: {obj.name}")
                        self.success_objects.append(obj.name)
                    except Exception as e:
                        print(f"Failed to apply modifier to {obj.name}: {e}")
                        self.failed_objects.append(f"{obj.name} (Ошибка: {e})")
                else:
                    # Если модификатор не найден на объекте
                    print(f"Modifier '{modifier_name_to_apply}' NOT FOUND on object: {obj.name}")
                    self.not_found_objects.append(obj.name)
        # Возвращаем исходный активный объект на место
        context.view_layer.objects.active = original_active

        # Вызов всплывающего окна через встроенный метод оператора
        context.window_manager.popup_menu(self.draw_popup, title="Результат операции", icon='INFO')
        return {'FINISHED'}

    # Функция отрисовки всплывающего окна
    def draw_popup(self, self_popup, context):
        layout = self_popup.layout
        # Если успешно применилось
        if self.success_objects:
            layout.label(text="Успешно применено к:", icon='CHECKMARK')
            for name in self.success_objects:
                layout.label(text=f" ➔ {name}")
        # Если были технические ошибки применения
        if self.failed_objects:
            if self.success_objects: layout.separator()
            layout.label(text="Ошибки применения:", icon='ERROR')
            for error_msg in self.failed_objects:
                layout.label(text=f" ➔ {error_msg}")
        # Если модификатор просто не был найден на объектах
        if self.not_found_objects:
            modifier_name_to_apply = context.scene.my_mod_settings.modifier_name
            if self.success_objects or self.failed_objects: layout.separator()
            layout.label(text=f"Модификатор '{modifier_name_to_apply}' не найден у:", icon='QUESTION')
            for name in self.not_found_objects:
                layout.label(text=f" ➔ {name}")

# ИНТЕРФЕЙС: Создаём панель на вкладке N- панели
class VIEW3D_PT_apply_specific_modifier_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Apply Mod' # Имя вкладки на N - панели
    bl_label = "Применение модификатора"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Поле для ввода имени модификатора на панели
        layout.prop(scene.my_mod_settings, "modifier_name")
        layout.separator()

        # Сама кнопка, которая запускает оператор
        layout.operator("object.apply_specific_modifier", icon='MODIFIER')

# Регистрация классов в Blender
classes = (
    MyModifierSettings,
    OBJECT_OT_apply_specific_modifier,
    VIEW3D_PT_apply_specific_modifier_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_mod_settings = bpy.props.PointerProperty(type=MyModifierSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.utils.unregister_class(cls)
    del bpy.types.Scene.my_mod_settings

if __name__ == "__main__":
    register()


