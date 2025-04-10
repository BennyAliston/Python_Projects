import json
import os
import uuid
from datetime import datetime, date

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp

# Set window size and background color
Window.size = (1000, 700)
Window.minimum_width = 800
Window.minimum_height = 600

# Load the kv file
Builder.load_file('main.kv')

class TaskListView(RecycleView):
    def __init__(self, **kwargs):
        super(TaskListView, self).__init__(**kwargs)
        self.data = []
        self.size_hint = (1, 1)  # Take up all available space

class TaskItem(RecycleDataViewBehavior, BoxLayout):
    task_id = StringProperty('')
    task_text = StringProperty('')
    deadline_text = StringProperty('')
    priority_text = StringProperty('')
    completed = BooleanProperty(False)
    selected = BooleanProperty(False)
    app = ObjectProperty(None)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.task_id = data.get('id', '')
        self.task_text = data.get('task', '')
        self.deadline_text = data.get('deadline', '')
        self.priority_text = data.get('priority', 'Medium')
        self.completed = data.get('completed', False)
        self.selected = data.get('selected', False)
        self.app = data.get('app', None)
        return super(TaskItem, self).refresh_view_attrs(rv, index, data)

    def toggle_complete(self):
        if self.app:
            self.app.toggle_task_complete(self.task_id)

    def toggle_select(self):
        if self.app:
            self.selected = not self.selected
            self.app.update_task(self.task_id, {'selected': self.selected})

    def delete_task(self):
        if self.app:
            self.app.remove_task(self.task_id)

    def edit_task(self):
        if not self.app:
            return

        content = GridLayout(cols=2, spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # Task input
        content.add_widget(Label(text="Task:", size_hint_x=0.3))
        task_input = TextInput(text=self.task_text, multiline=False, size_hint_y=None, height='40dp')
        content.add_widget(task_input)

        # Deadline input
        content.add_widget(Label(text="Deadline:", size_hint_x=0.3))
        deadline_input = TextInput(text=self.deadline_text, multiline=False, size_hint_y=None, height='40dp')
        content.add_widget(deadline_input)

        # Priority input
        content.add_widget(Label(text="Priority:", size_hint_x=0.3))
        priority_spinner = Spinner(
            text=self.priority_text,
            values=('Low', 'Medium', 'High'),
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(priority_spinner)

        # Error label
        error_label = Label(text="", color=(1, 0, 0, 1), size_hint_y=None, height='40dp')
        content.add_widget(error_label)
        content.add_widget(Widget())  # Empty widget for grid alignment

        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        save_button = Button(text="Save")
        cancel_button = Button(text="Cancel")
        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)

        # Add button layout with colspan=2
        content.add_widget(Widget())  # Empty widget for grid alignment
        content.add_widget(button_layout)

        popup = Popup(title="Edit Task",
                     content=content,
                     size_hint=(None, None),
                     size=(400, 300))

        def save_action(instance):
            new_text = task_input.text.strip()
            new_deadline = deadline_input.text.strip()
            new_priority = priority_spinner.text

            if not new_text:
                error_label.text = "Task text cannot be empty"
                return

            updates = {
                'task': new_text,
                'deadline': new_deadline,
                'priority': new_priority
            }
            self.app.update_task(self.task_id, updates)
            popup.dismiss()

        save_button.bind(on_press=save_action)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

class TodoLayout(BoxLayout):
    app = ObjectProperty(None)
    current_filter = StringProperty('All')
    current_theme = StringProperty('Light')

    def __init__(self, **kwargs):
        super(TodoLayout, self).__init__(**kwargs)
        Clock.schedule_once(self._init_ui, 0)

    def _init_ui(self, dt):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            if self.app:
                self.app.update_ui()

    def add_task_ui(self):
        task_text = self.ids.task_input.text.strip()
        deadline_str = self.ids.deadline_input.text.strip()
        priority = self.ids.priority_spinner.text

        if not task_text:
            return

        if not deadline_str:
            deadline_str = date.today().strftime("%d-%m-%Y")

        self.app.add_task(task_text, deadline_str, priority)
        self.ids.task_input.text = ''
        self.ids.deadline_input.text = ''
        self.ids.priority_spinner.text = 'Medium'

    def apply_filter(self, filter_value):
        self.current_filter = filter_value
        self.app.update_ui()

    def apply_theme(self, theme):
        self.current_theme = theme
        # Update theme-related properties here
        self.app.update_ui()

    def search_tasks(self, search_text):
        # Update the task list based on search text
        self.app.update_ui(search_text)

    def remove_selected(self):
        self.app.remove_selected_tasks()

class TodoApp(App):
    tasks = ListProperty([])
    tasks_file = StringProperty('tasks.json')

    def __init__(self, **kwargs):
        super(TodoApp, self).__init__(**kwargs)
        self.title = 'To-Do List Manager'

    def build(self):
        self.tasks_file = os.path.join(os.path.dirname(__file__), 'tasks.json')
        self.load_tasks()
        return TodoLayout(app=self)

    def update_ui(self, search_text=''):
        if not self.root:
            return

        filtered_tasks = self.tasks

        # Apply search filter
        if search_text:
            filtered_tasks = [
                task for task in filtered_tasks
                if search_text.lower() in task['task'].lower()
            ]

        # Apply status filter
        if self.root.current_filter != 'All':
            is_completed = self.root.current_filter == 'Completed'
            filtered_tasks = [
                task for task in filtered_tasks
                if task.get('completed', False) == is_completed
            ]

        # Update task list
        if hasattr(self.root.ids, 'task_list'):
            task_list = self.root.ids.task_list
            task_list.data = []
            for task in filtered_tasks:
                task_data = task.copy()
                task_data['app'] = self
                task_list.data.append(task_data)

        # Update status bar
        if hasattr(self.root.ids, 'status_bar'):
            total = len(self.tasks)
            completed = sum(1 for task in self.tasks if task.get('completed', False))
            pending = total - completed
            percentage = (completed / total * 100) if total > 0 else 0
            self.root.ids.status_bar.text = f"Total: {total} | Completed: {completed} | Pending: {pending} ({percentage:.0f}%)"

    def remove_selected_tasks(self):
        self.tasks = [task for task in self.tasks if not task.get('selected', False)]
        self.save_tasks()
        self.update_ui()

    def load_tasks(self):
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            else:
                self.tasks = []
                
            # Add sample task if list is empty
            if not self.tasks:
                self.tasks.append({
                    'id': str(uuid.uuid4()),
                    'task': 'Sample Task - Click checkbox to complete',
                    'deadline': date.today().strftime("%d-%m-%Y"),
                    'priority': 'Medium',
                    'completed': False
                })
                self.save_tasks()
                
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []

    def save_tasks(self):
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=4)
        except Exception as e:
            print(f"Error saving tasks: {e}")
            # Show error to user through status bar
            if self.root and hasattr(self.root, 'status_bar'):
                self.root.status_bar.text = f"Error saving tasks: {e}"

    def add_task(self, task_text, deadline_str, priority):
        new_task = {
            'id': str(uuid.uuid4()),
            'task': task_text,
            'deadline': deadline_str,
            'priority': priority,
            'completed': False
        }
        self.tasks.append(new_task)
        self.save_tasks()
        self.update_ui()

    def update_task(self, task_id, updates):
        for i, task in enumerate(self.tasks):
            if task.get('id') == task_id:
                self.tasks[i].update(updates)
                self.save_tasks()
                self.update_ui()
                break

    def toggle_task_complete(self, task_id):
        for task in self.tasks:
            if task.get('id') == task_id:
                task['completed'] = not task.get('completed', False)
                self.save_tasks()
                self.update_ui()
                break

    def remove_task(self, task_id):
        original_length = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.get('id') != task_id]
        if len(self.tasks) < original_length:
            self.save_tasks()
            self.update_ui()

if __name__ == "__main__":
    TodoApp().run()