#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from db import Memory, DBProvider, current_time

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

        self.time.set_text(self.memory.time_str())
        self.content.set_text(self.memory.content)
        self.feeling.set_text(self.memory.feeling)
        self.title.set_text(self.memory.title)

        self.right_click_menu = Gtk.Menu()
        delete_item = Gtk.ImageMenuItem(label=Gtk.STOCK_DELETE)
        edit_item = Gtk.ImageMenuItem(label=Gtk.STOCK_EDIT)
        delete_item.set_use_stock(True)
        edit_item.set_use_stock(True)
        self.right_click_menu.append(delete_item)
        self.right_click_menu.append(edit_item)
        delete_item.connect('button-press-event', self.delete)
        edit_item.connect('button-press-event', self.edit)
        self.right_click_menu.show_all()

        self.show()
        self.connect('button-press-event', self.on_click)

    def sync_with_memory(self):
        self.time.set_text(self.memory.time_str())
        self.content.set_text(self.memory.content)
        self.feeling.set_text(self.memory.feeling)
        self.title.set_text(self.memory.title)

    def edit(self, widget, event):
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

        self.memory = None

        self.title = builder.get_object('title')
        self.content = builder.get_object('content')
        self.feeling = builder.get_object('feeling')
        self.cancel = builder.get_object('cancel')
        self.save = builder.get_object('save')

        self.save.connect('clicked', lambda _ : self.save_memory())
        self.cancel.connect("clicked", lambda _ : self.window.switch_to_home())

        self.show_all()

    def save_memory(self):
        self.memory.content = self.content.get_buffer().get_text(
            self.content.get_buffer().get_start_iter(),
            self.content.get_buffer().get_end_iter(),
            True)
        self.memory.title = self.title.get_text()
        self.memory.feeling = self.feeling.get_text()
        if self.memory.in_db():
            self.window.db_provider.update_memory(self.memory)
            self.window.update_memory(self.memory)
        else:
            self.window.db_provider.add_memory(self.memory)
            self.window.add_memory(self.memory)

    def set_memory(self, memory):
        self.memory = memory
        self.title.set_text(memory.title)
        self.content.get_buffer().set_text(memory.content)
        self.feeling.set_text(memory.feeling)

class Window(Gtk.Window):
    def __init__(self, db_provider):
        Gtk.Window.__init__(self)
        self.db_provider = db_provider
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

        mems = self.db_provider.get_memories()
        for memory in mems:
            self.add_memory(memory)

        self.new_memory_button.connect('clicked', lambda _ :
                                       self.switch_to_editor_with_new_memory())

        self.show_all()

    def set_editor_memory(self, memory):
        self.editor_memory = memory

    def add_memory(self, memory):
        self.memories_container.add(MemoryWidget(self, memory))

    def update_memory(self, memory):
        for parent_widget in self.memories_container.get_children():
            memory_widget = parent_widget.get_child()
            if memory_widget.memory == memory:
                memory_widget.sync_with_memory()

    def remove_memory(self, memory):
        self.db_provider.delete_memory(memory)
        for parent_widget in self.memories_container.get_children():
            memory_widget = parent_widget.get_child()
            if memory_widget.memory == memory:
                self.memories_container.remove(parent_widget)

    def switch_to_editor_with_new_memory(self):
        self.editor.set_memory(Memory('', '', '', current_time()))
        self.switch_to_editor()

    def switch_to_editor(self):
        self.remove(self.home_widget)
        self.add(self.editor)

    def switch_to_home(self):
        self.remove(self.editor)
        self.add(self.home_widget)

if __name__ == '__main__':
    db_provider = DBProvider('memories.db')
    Window(db_provider)
    Gtk.main()
