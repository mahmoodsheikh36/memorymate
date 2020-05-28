#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Memory:
    def __init__(self, title, content, feeling, time):
        self.title = title
        self.content = content
        self.time = time
        self.feeling = feeling

class MemoryWidget(Gtk.EventBox):
    def __init__(self, window, memory):
        Gtk.Widget.__init__(self)
        self.window = window
        self.memory = memory

        builder = Gtk.Builder()
        builder.add_from_file('ui_data/memory.glade')
        self.add(builder.get_object('memory'))

        self.title = builder.get_object('title')
        self.content = builder.get_object('content')
        self.time = builder.get_object('time')
        self.feeling = builder.get_object('feeling')

        self.time.set_text(self.memory.time)
        self.content.set_text(self.memory.content)
        self.feeling.set_text(self.memory.feeling)
        self.title.set_text(self.memory.title)

        self.right_click_menu = Gtk.Menu()
        delete_item = Gtk.MenuItem(label='delete')
        self.right_click_menu.append(delete_item)
        delete_item.connect('button-press-event', self.delete)
        delete_item.show()

        self.show()
        self.connect('button-press-event', self.on_click)

    def edit(self):
        self.window.editor.set_memory(self.memory)
        self.window.switch_to_editor()

    def delete(self, widget, event):
        self.window.remove_memory(self.memory)

    def on_click(self, widget, event):
        if event.button == 3: # right click
            self.right_click_menu.popup(None, None, None, None, event.button, event.time)

class MemoryEditor(Gtk.EventBox):
    def __init__(self, window):
        Gtk.EventBox.__init__(self)
        self.window = window

        builder = Gtk.Builder()
        builder.add_from_file('ui_data/editor.glade')
        self.add(builder.get_object('editor'))

        self.title = builder.get_object('title')
        self.content = builder.get_object('content')
        self.feeling = builder.get_object('feeling')
        self.cancel = builder.get_object('cancel')
        self.save = builder.get_object('save')

        self.cancel.connect("clicked", lambda _ : self.window.switch_to_home())

        self.show_all()

    def set_memory(self, memory):
        self.memory = memory
        self.title.set_text(memory.title)
        self.content.get_buffer().set_text(memory.content)
        self.feeling.set_text(memory.feeling)

class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_title('memorymate')
        self.connect("destroy", Gtk.main_quit)

        builder = Gtk.Builder()
        builder.add_from_file("ui_data/home.glade")

        self.home_widget = builder.get_object('home')
        self.editor = MemoryEditor(self)
        self.cancel_editor_button = builder.get_object('cancel_editor')
        self.save_editor_button = builder.get_object('save_editor')
        self.new_memory_button = builder.get_object('new_memory')
        self.add(self.home_widget)

        self.memories_container = builder.get_object('memories')
        memory1 = Memory('some title for this memory',
                         'hey',
                         'was feeling happy',
                         '2 mins ago')
        memory2 = Memory('sunny day test 1', 'hi hi hi hi hi some memory',
                         'was feeling happy', '18 mins ago')
        memory3 = Memory('sunny day test 2', 'whatever',
                         'was feeling sad', '17 years ago')
        self.add_memory(memory1)
        self.add_memory(memory2)
        self.add_memory(memory3)
        self.editor.set_memory(memory1)

        self.new_memory_button.connect('clicked', lambda _ : self.switch_to_editor())

        self.show_all()

    def set_editor_memory(self, memory):
        self.editor_memory = memory

    def add_memory(self, memory):
        self.memories_container.add(MemoryWidget(self, memory))

    def remove_memory(self, memory):
        for parent_widget in self.memories_container.get_children():
            memory_widget = parent_widget.get_child()
            if memory_widget.memory == memory:
                self.memories_container.remove(parent_widget)

    def switch_to_editor(self):
        self.remove(self.home_widget)
        self.add(self.editor)

    def switch_to_home(self):
        self.remove(self.editor)
        self.add(self.home_widget)

if __name__ == '__main__':
    Window()
    Gtk.main()
