"""
Редактор деталей ракеты с пользовательской клавиатурой
Версия для Pydroid 3 с полностью отключенной системной клавиатурой
"""
import os
import json
from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock
from functools import partial

# Принудительно используем свою клавиатуру вместо системной
# ОБЯЗАТЕЛЬНО УСТАНОВИТЬ ПЕРЕД ИМПОРТОМ Config
os.environ['KIVY_USE_ANDROID_KEYBOARD'] = '0'
os.environ['KIVY_NO_NATIVE_KEYBOARD'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'

# Теперь можно импортировать Config
from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'dock')
Config.set('graphics', 'resizable', '0')

# Переменная для проверки Android-платформы
IS_ANDROID = os.path.exists('/data/data')

# Класс встроенной клавиатуры для модальных окон
class ModalKeyboard(BoxLayout):
    def __init__(self, textinput, **kwargs):
        super(ModalKeyboard, self).__init__(orientation='vertical', size_hint=(1, None), height=dp(200), **kwargs)
        self.textinput = textinput
        self.is_caps = False
        self.is_russian = True
        
        # Создаем русскую раскладку
        self.russian_layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '.'],
            ['й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х'],
            ['ф', 'ы', 'в', 'а', 'п', 'р', 'о', 'л', 'д', 'ж', 'э'],
            ['я', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б', 'ю', ',']
        ]
        
        # Создаем английскую раскладку
        self.english_layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '.'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.']
        ]
        
        # Создаем клавиатуру
        self.keyboard_layout = GridLayout(cols=1)
        self.add_widget(self.keyboard_layout)
        self.build_keyboard()
        
    def build_keyboard(self):
        # Очищаем предыдущую клавиатуру
        self.keyboard_layout.clear_widgets()
        
        # Выбираем текущую раскладку
        current_layout = self.russian_layout if self.is_russian else self.english_layout
        
        # Создаем строки клавиатуры
        for row in current_layout:
            row_layout = BoxLayout(size_hint_y=None, height=dp(40))
            
            # Добавляем кнопки в строку
            for key in row:
                displayed_key = key.upper() if self.is_caps else key
                btn = Button(text=displayed_key)
                btn.bind(on_press=lambda x, k=displayed_key: self.key_pressed(k))
                row_layout.add_widget(btn)
                
            self.keyboard_layout.add_widget(row_layout)
        
        # Добавляем специальные кнопки
        special_row = BoxLayout(size_hint_y=None, height=dp(40))
        
        # Кнопка переключения языка
        lang_btn = Button(text="RU/EN" if self.is_russian else "EN/RU", size_hint_x=0.2)
        lang_btn.bind(on_press=self.switch_language)
        
        # Кнопка Caps Lock
        caps_btn = Button(text="CAPS", size_hint_x=0.2)
        caps_btn.bind(on_press=self.toggle_caps)
        
        # Кнопка пробела
        space_btn = Button(text="ПРОБЕЛ", size_hint_x=0.4)
        space_btn.bind(on_press=lambda x: self.key_pressed(" "))
        
        # Кнопка удаления
        backspace_btn = Button(text="←", size_hint_x=0.2)
        backspace_btn.bind(on_press=self.backspace)
        
        special_row.add_widget(lang_btn)
        special_row.add_widget(caps_btn)
        special_row.add_widget(space_btn)
        special_row.add_widget(backspace_btn)
        
        self.keyboard_layout.add_widget(special_row)
    
    def key_pressed(self, key):
        """Обработка нажатия на клавишу"""
        if self.textinput:
            self.textinput.text += key
    
    def backspace(self, instance):
        """Обработка нажатия на backspace"""
        if self.textinput and self.textinput.text:
            self.textinput.text = self.textinput.text[:-1]
    
    def toggle_caps(self, instance):
        """Переключение регистра"""
        self.is_caps = not self.is_caps
        self.build_keyboard()
    
    def switch_language(self, instance):
        """Переключение языка"""
        self.is_russian = not self.is_russian
        self.build_keyboard()

# Всплывающее окно выбора папки
class FolderSelectionModal(ModalView):
    def __init__(self, parent_modal, **kwargs):
        super(FolderSelectionModal, self).__init__(size_hint=(0.9, 0.9), auto_dismiss=True, **kwargs)
        self.parent_modal = parent_modal
        
        # Создаем верхнюю часть с вводом и кнопками
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Добавляем заголовок
        main_layout.add_widget(Label(text="Укажите имя новой папки:", size_hint_y=None, height=40))
        
        # Поле ввода
        self.folder_input = TextInput(
            hint_text="Имя папки", 
            multiline=False, 
            size_hint_y=None, 
            height=60,
            readonly=True  # Делаем поле только для чтения, чтобы предотвратить показ системной клавиатуры
        )
        self.folder_input.bind(focus=self.on_focus)
        main_layout.add_widget(self.folder_input)
        
        # Кнопки подтверждения и отмены
        button_layout = BoxLayout(size_hint_y=None, height=60)
        confirm_button = Button(text="Подтвердить")
        confirm_button.bind(on_release=self.confirm_selection)
        cancel_button = Button(text="Отменить")
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        main_layout.add_widget(button_layout)
        
        # Добавляем встроенную клавиатуру
        self.keyboard = ModalKeyboard(self.folder_input)
        main_layout.add_widget(self.keyboard)
        
        self.add_widget(main_layout)
    
    def on_focus(self, instance, value):
        """Обработка фокуса на поле ввода"""
        # Для предотвращения появления системной клавиатуры
        pass
    
    def confirm_selection(self, instance):
        folder_name = self.folder_input.text.strip()
        if folder_name:
            self.parent_modal.save_to_folder(folder_name)
        else:
            print("Необходимо указать имя папки.")
        self.dismiss()

# Класс для ввода числовых значений
class NumberInputModal(ModalView):
    def __init__(self, title, initial_value, callback, **kwargs):
        super(NumberInputModal, self).__init__(size_hint=(0.9, 0.8), auto_dismiss=True, **kwargs)
        self.callback = callback
        self.initial_value = str(initial_value)
        
        # Создаем основной макет
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Добавляем заголовок
        main_layout.add_widget(Label(text=title, size_hint_y=None, height=40))
        
        # Поле ввода
        self.value_input = TextInput(
            text=self.initial_value, 
            multiline=False, 
            readonly=True,  # Делаем поле только для чтения, чтобы предотвратить показ системной клавиатуры
            font_size=20,
            size_hint_y=None, 
            height=60
        )
        self.value_input.bind(focus=self.on_focus)
        main_layout.add_widget(self.value_input)
        
        # Кнопки подтверждения и отмены
        button_layout = BoxLayout(size_hint_y=None, height=60)
        confirm_button = Button(text="Подтвердить")
        confirm_button.bind(on_release=self.confirm_selection)
        cancel_button = Button(text="Отменить")
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        main_layout.add_widget(button_layout)
        
        # Добавляем числовую клавиатуру
        num_keyboard = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
        
        # Создаем ряды с числами
        rows = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', '.', '-']
        ]
        
        for row in rows:
            row_layout = BoxLayout(size_hint_y=None, height=dp(40))
            for key in row:
                btn = Button(text=key)
                btn.bind(on_press=lambda x, k=key: self.key_pressed(k))
                row_layout.add_widget(btn)
            num_keyboard.add_widget(row_layout)
        
        # Добавляем строку с кнопкой удаления
        special_row = BoxLayout(size_hint_y=None, height=dp(40))
        clear_btn = Button(text="Очистить", size_hint_x=0.5)
        clear_btn.bind(on_press=self.clear_input)
        backspace_btn = Button(text="←", size_hint_x=0.5)
        backspace_btn.bind(on_press=self.backspace)
        special_row.add_widget(clear_btn)
        special_row.add_widget(backspace_btn)
        num_keyboard.add_widget(special_row)
        
        main_layout.add_widget(num_keyboard)
        
        self.add_widget(main_layout)
    
    def on_focus(self, instance, value):
        """Обработка фокуса на поле ввода"""
        # Для предотвращения появления системной клавиатуры
        pass
    
    def key_pressed(self, key):
        """Обработка нажатия на клавишу"""
        # Специальная обработка для чисел с плавающей точкой
        if key == '.' and '.' in self.value_input.text:
            return  # Предотвращаем добавление второй точки
        elif key == '-' and self.value_input.text:
            if self.value_input.text[0] == '-':
                self.value_input.text = self.value_input.text[1:]  # Убираем минус
            else:
                self.value_input.text = '-' + self.value_input.text  # Добавляем минус
            return
        
        self.value_input.text += key
    
    def backspace(self, instance):
        """Обработка нажатия на backspace"""
        if self.value_input.text:
            self.value_input.text = self.value_input.text[:-1]
    
    def clear_input(self, instance):
        """Очистка поля ввода"""
        self.value_input.text = ""
    
    def confirm_selection(self, instance):
        try:
            value = float(self.value_input.text) if self.value_input.text else 0
            self.callback(value)
            self.dismiss()
        except ValueError:
            # Показываем сообщение об ошибке
            error_popup = ModalView(size_hint=(0.8, 0.3))
            error_layout = BoxLayout(orientation='vertical', padding=10)
            error_layout.add_widget(Label(text="Неверный формат числа."))
            close_button = Button(text="Закрыть", size_hint_y=None, height=50)
            close_button.bind(on_release=error_popup.dismiss)
            error_layout.add_widget(close_button)
            error_popup.add_widget(error_layout)
            error_popup.open()

# Диалоговое окно запроса текста
class TextInputModal(ModalView):
    def __init__(self, title, initial_text, callback, **kwargs):
        super(TextInputModal, self).__init__(size_hint=(0.9, 0.9), auto_dismiss=True, **kwargs)
        self.callback = callback
        
        # Основной макет
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        main_layout.add_widget(Label(text=title, size_hint_y=None, height=40))
        
        # Текстовое поле для ввода
        self.text_input = TextInput(
            text=initial_text,
            multiline=True,
            readonly=True,  # Делаем поле только для чтения для предотвращения вызова системной клавиатуры
            size_hint_y=None,
            height=dp(100)
        )
        self.text_input.bind(focus=self.on_focus)
        main_layout.add_widget(self.text_input)
        
        # Кнопки подтверждения и отмены
        button_layout = BoxLayout(size_hint_y=None, height=dp(50))
        confirm_button = Button(text="Подтвердить")
        confirm_button.bind(on_release=self.confirm)
        cancel_button = Button(text="Отменить")
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        main_layout.add_widget(button_layout)
        
        # Добавляем нашу кастомную клавиатуру
        self.keyboard = ModalKeyboard(self.text_input)
        main_layout.add_widget(self.keyboard)
        
        self.add_widget(main_layout)
    
    def on_focus(self, instance, value):
        """Обработка фокуса на поле ввода"""
        # Для предотвращения появления системной клавиатуры
        pass
    
    def confirm(self, instance):
        """Подтверждение ввода"""
        text = self.text_input.text
        self.callback(text)
        self.dismiss()

# Главный класс для отображения списка деталей ракеты
class RocketPartsEditor(GridLayout):
    def __init__(self, **kwargs):
        super(RocketPartsEditor, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.padding = 20
        
        # Путь к папке с данными
        self.data_folder = "rocket_data"
        self.current_folder = None
        
        # Создаём папку, если её нет
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        # Структура для хранения деталей ракеты
        self.rocket_parts = []
        
        # Шаблон новой детали
        self.default_part = {
            "name": "Новая деталь",
            "weight": 0.0,
            "length": 0.0,
            "diameter": 0.0,
            "material": "Алюминий",
            "is_critical": False,
            "notes": ""
        }
        
        # Верхняя часть с кнопками управления и выбором папки
        top_controls = BoxLayout(size_hint_y=None, height=dp(100))
        
        # Добавляем спиннер для выбора папки с деталями
        folder_layout = BoxLayout(orientation='vertical')
        folder_layout.add_widget(Label(text="Выберите папку:"))
        
        self.folder_spinner = Spinner(
            text='Выберите папку',
            values=self.get_folders(),
            size_hint_y=None,
            height=dp(50)
        )
        self.folder_spinner.bind(text=self.on_folder_select)
        folder_layout.add_widget(self.folder_spinner)
        
        top_controls.add_widget(folder_layout)
        
        # Кнопки управления папками
        folder_buttons = BoxLayout(orientation='vertical')
        
        new_folder_btn = Button(text="Новая папка", size_hint_y=None, height=dp(50))
        new_folder_btn.bind(on_press=self.create_new_folder)
        folder_buttons.add_widget(new_folder_btn)
        
        save_btn = Button(text="Сохранить", size_hint_y=None, height=dp(50))
        save_btn.bind(on_press=self.save_data)
        folder_buttons.add_widget(save_btn)
        
        top_controls.add_widget(folder_buttons)
        
        self.add_widget(top_controls)
        
        # Добавляем кнопку для создания новой детали
        add_button = Button(text="Добавить новую деталь", size_hint_y=None, height=dp(60))
        add_button.bind(on_press=self.add_new_part)
        self.add_widget(add_button)
        
        # Контейнер для прокрутки списка деталей
        scroll_container = ScrollView()
        
        # Контейнер для списка деталей
        self.parts_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.parts_list.bind(minimum_height=self.parts_list.setter('height'))
        
        scroll_container.add_widget(self.parts_list)
        self.add_widget(scroll_container)
        
        # Если есть папки, выбираем первую
        if self.folder_spinner.values:
            self.folder_spinner.text = self.folder_spinner.values[0]
            self.on_folder_select(self.folder_spinner, self.folder_spinner.text)
    
    def get_folders(self):
        """Получить список папок с данными о ракетах"""
        folders = []
        if os.path.exists(self.data_folder):
            for item in os.listdir(self.data_folder):
                folder_path = os.path.join(self.data_folder, item)
                if os.path.isdir(folder_path):
                    folders.append(item)
        return folders
    
    def on_folder_select(self, spinner, text):
        """Обработка выбора папки"""
        if text != 'Выберите папку':
            self.current_folder = text
            self.load_data()
            self.update_parts_list()
    
    def create_new_folder(self, instance):
        """Создание новой папки"""
        folder_modal = FolderSelectionModal(self)
        folder_modal.open()
    
    def save_to_folder(self, folder_name):
        """Сохранение данных в новую папку"""
        # Создаём папку
        folder_path = os.path.join(self.data_folder, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Обновляем спиннер и выбираем новую папку
        folders = self.get_folders()
        self.folder_spinner.values = folders
        self.folder_spinner.text = folder_name
        self.current_folder = folder_name
        
        # Создаём пустой список деталей
        self.rocket_parts = []
        self.save_data()
        self.update_parts_list()
    
    def load_data(self):
        """Загрузка данных из файла"""
        if not self.current_folder:
            return
        
        file_path = os.path.join(self.data_folder, self.current_folder, "parts.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.rocket_parts = json.load(f)
            except:
                self.rocket_parts = []
        else:
            self.rocket_parts = []
    
    def save_data(self, instance=None):
        """Сохранение данных в файл"""
        if not self.current_folder:
            return
        
        folder_path = os.path.join(self.data_folder, self.current_folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        file_path = os.path.join(folder_path, "parts.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.rocket_parts, f, ensure_ascii=False, indent=4)
    
    def add_new_part(self, instance):
        """Добавление новой детали"""
        # Создаём копию шаблона
        new_part = self.default_part.copy()
        self.rocket_parts.append(new_part)
        self.update_parts_list()
    
    def update_parts_list(self):
        """Обновление списка деталей на экране"""
        self.parts_list.clear_widgets()
        
        for i, part in enumerate(self.rocket_parts):
            # Создаём карточку для детали
            part_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180), padding=5)
            
            # Верхняя строка с названием и кнопкой удаления
            header = BoxLayout(size_hint_y=None, height=dp(40))
            
            # Название детали с возможностью редактирования
            name_button = Button(text=part["name"], size_hint_x=0.8)
            name_button.part_index = i  # Сохраняем индекс детали
            name_button.bind(on_press=lambda btn: self.edit_text_property(btn.part_index, "name", "Название детали"))
            
            # Кнопка удаления
            delete_button = Button(text="Удалить", size_hint_x=0.2)
            delete_button.part_index = i
            delete_button.bind(on_press=self.delete_part)
            
            header.add_widget(name_button)
            header.add_widget(delete_button)
            part_card.add_widget(header)
            
            # Основные свойства
            properties_layout = GridLayout(cols=2)
            
            # Вес
            properties_layout.add_widget(Label(text="Вес (кг):"))
            weight_button = Button(text=str(part["weight"]))
            weight_button.part_index = i
            weight_button.bind(on_press=lambda btn: self.edit_number_property(btn.part_index, "weight", "Вес детали (кг)"))
            properties_layout.add_widget(weight_button)
            
            # Длина
            properties_layout.add_widget(Label(text="Длина (м):"))
            length_button = Button(text=str(part["length"]))
            length_button.part_index = i
            length_button.bind(on_press=lambda btn: self.edit_number_property(btn.part_index, "length", "Длина детали (м)"))
            properties_layout.add_widget(length_button)
            
            # Диаметр
            properties_layout.add_widget(Label(text="Диаметр (м):"))
            diameter_button = Button(text=str(part["diameter"]))
            diameter_button.part_index = i
            diameter_button.bind(on_press=lambda btn: self.edit_number_property(btn.part_index, "diameter", "Диаметр детали (м)"))
            properties_layout.add_widget(diameter_button)
            
            # Материал
            properties_layout.add_widget(Label(text="Материал:"))
            material_spinner = Spinner(
                text=part["material"],
                values=("Алюминий", "Титан", "Сталь", "Композит", "Другое")
            )
            material_spinner.part_index = i
            material_spinner.bind(text=self.on_material_select)
            properties_layout.add_widget(material_spinner)
            
            part_card.add_widget(properties_layout)
            
            # Дополнительные свойства
            bottom_layout = BoxLayout()
            
            # Критическая важность
            critical_layout = BoxLayout(orientation='vertical')
            critical_layout.add_widget(Label(text="Критически важная:"))
            critical_check = CheckBox(active=part["is_critical"])
            critical_check.part_index = i
            critical_check.bind(active=self.on_critical_toggle)
            critical_layout.add_widget(critical_check)
            bottom_layout.add_widget(critical_layout)
            
            # Заметки
            notes_layout = BoxLayout(orientation='vertical')
            notes_layout.add_widget(Label(text="Заметки:"))
            notes_button = Button(text="Редактировать")
            notes_button.part_index = i
            notes_button.bind(on_press=lambda btn: self.edit_text_property(btn.part_index, "notes", "Заметки о детали"))
            notes_layout.add_widget(notes_button)
            bottom_layout.add_widget(notes_layout)
            
            part_card.add_widget(bottom_layout)
            
            # Добавляем карточку в список
            self.parts_list.add_widget(part_card)
    
    def delete_part(self, instance):
        """Удаление детали из списка"""
        index = instance.part_index
        if 0 <= index < len(self.rocket_parts):
            del self.rocket_parts[index]
            self.update_parts_list()
    
    def edit_number_property(self, part_index, property_name, title):
        """Редактирование числового свойства"""
        if 0 <= part_index < len(self.rocket_parts):
            current_value = self.rocket_parts[part_index][property_name]
            
            def update_property(new_value):
                self.rocket_parts[part_index][property_name] = new_value
                self.update_parts_list()
            
            number_modal = NumberInputModal(title, current_value, update_property)
            number_modal.open()
    
    def edit_text_property(self, part_index, property_name, title):
        """Редактирование текстового свойства"""
        if 0 <= part_index < len(self.rocket_parts):
            current_text = self.rocket_parts[part_index][property_name]
            
            def update_property(new_text):
                self.rocket_parts[part_index][property_name] = new_text
                self.update_parts_list()
            
            text_modal = TextInputModal(title, current_text, update_property)
            text_modal.open()
    
    def on_material_select(self, spinner, text):
        """Обработка выбора материала"""
        part_index = spinner.part_index
        if 0 <= part_index < len(self.rocket_parts):
            self.rocket_parts[part_index]["material"] = text
    
    def on_critical_toggle(self, checkbox, value):
        """Обработка изменения флага критически важной детали"""
        part_index = checkbox.part_index
        if 0 <= part_index < len(self.rocket_parts):
            self.rocket_parts[part_index]["is_critical"] = value

# Главное приложение
class RocketEditorApp(App):
    def build(self):
        self.title = "Редактор деталей ракеты"
        
        # Устанавливаем размер окна на настольных системах
        # Только если мы не в среде GitHub Actions
        if not IS_ANDROID and 'GITHUB_ACTIONS' not in os.environ:
            from kivy.core.window import Window
            Window.size = (480, 800)
        
        return RocketPartsEditor()

# Запуск приложения
if __name__ == "__main__":
    # Проверяем, находимся ли мы в GitHub Actions
    if 'GITHUB_ACTIONS' in os.environ:
        print("Запуск в GitHub Actions, пропускаем запуск приложения")
    else:
        app = RocketEditorApp()
        app.run()
