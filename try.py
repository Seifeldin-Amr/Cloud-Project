from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Line, Rectangle
import os
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog
import math
from kivy.config import Config

class Rotating3DBox(Widget):
    def __init__(self, **kwargs):
        super(Rotating3DBox, self).__init__(**kwargs)
        self.angle = 0
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        Clock.schedule_interval(self.animate, 1 / 60.)

    def project(self, x, y, z, fov, viewer_distance):
        factor = fov / (viewer_distance + z)
        x = x * factor + self.center_x
        y = -y * factor + self.center_y
        return x, y

    def update_graphics(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.0, 0.0, 0.0, 1)  # Set full black background
            Rectangle(pos=self.pos, size=self.size)
            Color(0.0, 1.0, 0.0, 1)

            size = min(self.width, self.height) * 0.25
            vertices = [
                [-size, -size, -size],
                [ size, -size, -size],
                [ size,  size, -size],
                [-size,  size, -size],
                [-size, -size,  size],
                [ size, -size,  size],
                [ size,  size,  size],
                [-size,  size,  size],
            ]

            angle_x = math.radians(self.angle)
            angle_y = math.radians(self.angle)
            angle_z = math.radians(self.angle)

            def rotate(x, y, z):
                y, z = y * math.cos(angle_x) - z * math.sin(angle_x), y * math.sin(angle_x) + z * math.cos(angle_x)
                x, z = x * math.cos(angle_y) + z * math.sin(angle_y), -x * math.sin(angle_y) + z * math.cos(angle_y)
                x, y = x * math.cos(angle_z) - y * math.sin(angle_z), x * math.sin(angle_z) + y * math.cos(angle_z)
                return x, y, z

            projected = [self.project(*rotate(x, y, z), fov=256, viewer_distance=4*size) for x, y, z in vertices]

            edges = [
                (0,1), (1,2), (2,3), (3,0),
                (4,5), (5,6), (6,7), (7,4),
                (0,4), (1,5), (2,6), (3,7)
            ]
            for edge in edges:
                Line(points=[*projected[edge[0]], *projected[edge[1]]], width=2)

    def animate(self, dt):
        self.angle += 1
        self.update_graphics()

class IntroScreen(Screen):
    def on_enter(self):
        layout = BoxLayout(orientation="vertical", padding=50)
        with layout.canvas.before:
            Color(0.0, 0.0, 0.0, 1)  # Full black screen background
            self.bg_rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_bg, pos=self._update_bg)
        self.add_widget(layout)

        self.box_widget = Rotating3DBox(size_hint=(1, 1))
        layout.add_widget(self.box_widget)

        self.start_btn = Button(
            text="Start",
            size_hint=(0.5, None),
            height=50,
            background_color=(0.3, 0.7, 1, 1),
            pos_hint={'center_x': 0.5}
        )
        self.start_btn.bind(on_press=self.start_app)
        layout.add_widget(self.start_btn)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def start_app(self, instance):
        self.manager.current = "disk"

# Disk Creation screen
class DiskScreen(Screen):
    def __init__(self, **kwargs):
        super(DiskScreen, self).__init__(**kwargs)
        
        # Main container with padding
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        self.add_widget(self.layout)

        # Title
        title = Label(
            text="Create Virtual Disk",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint=(1, None),
            height=50
        )
        self.layout.add_widget(title)

        # Form container with proper spacing
        self.form = GridLayout(
            cols=2,
            spacing=20,
            padding=20,
            size_hint=(1, None),
            height=300
        )
        
        # Add form elements with proper spacing
        form_elements = [
            ("Disk Size (GB):", "10", "text"),
            ("Disk Format:", "qcow2", "spinner"),
            ("Storage Path:", os.path.expanduser("~/vm_disks"), "text"),
            ("Disk Name:", "vm_disk", "text")
        ]
        
        for label_text, default_value, input_type in form_elements:
            # Label
            label = Label(
                text=label_text,
                font_size=20,
                color=(1, 1, 1, 1),
                size_hint=(0.4, None),
                height=40
            )
            self.form.add_widget(label)
            
            # Input field container for storage path
            if label_text == "Storage Path:":
                input_container = BoxLayout(orientation="horizontal", spacing=10, size_hint=(0.6, None), height=40)
                
                # Text input
                input_field = TextInput(
                    text=default_value,
                    multiline=False,
                    font_size=20,
                    size_hint=(0.7, 1),
                    background_color=(0.2, 0.2, 0.2, 1),
                    foreground_color=(1, 1, 1, 1)
                )
                
                # Browse button
                browse_btn = Button(
                    text="Browse",
                    size_hint=(0.3, 1),
                    background_color=(0.3, 0.7, 1, 1),
                    font_size=16
                )
                browse_btn.bind(on_press=lambda x: self.browse_directory(input_field))
                
                input_container.add_widget(input_field)
                input_container.add_widget(browse_btn)
                self.form.add_widget(input_container)
                self.storage_input = input_field
            else:
                # Regular input field
                if input_type == "text":
                    input_field = TextInput(
                        text=default_value,
                        multiline=False,
                        font_size=20,
                        size_hint=(0.6, None),
                        height=40,
                        background_color=(0.2, 0.2, 0.2, 1),
                        foreground_color=(1, 1, 1, 1)
                    )
                elif input_type == "spinner":
                    input_field = Spinner(
                        text=default_value,
                        values=["qcow2", "raw", "vmdk", "vhdx"],
                        font_size=20,
                        size_hint=(0.6, None),
                        height=40,
                        background_color=(0.2, 0.2, 0.2, 1),
                        color=(1, 1, 1, 1)
                    )
                
                self.form.add_widget(input_field)
            
            # Store reference to input field
            if label_text == "Disk Size (GB):":
                self.disk_input = input_field
            elif label_text == "Disk Format:":
                self.disk_format_input = input_field
            elif label_text == "Disk Name:":
                self.disk_name_input = input_field

        # Add form to scroll view
        scroll = ScrollView(
            size_hint=(1, 0.7),
            do_scroll_x=False
        )
        scroll.add_widget(self.form)
        self.layout.add_widget(scroll)

        # Button container
        button_container = BoxLayout(orientation="horizontal", spacing=20, size_hint=(1, None), height=60)
        
        # Next button
        self.next_btn = Button(
            text="Next",
            size_hint=(1, 1),
            background_color=(0.3, 0.7, 1, 1),
            font_size=24
        )
        self.next_btn.bind(on_press=self.next_screen)
        button_container.add_widget(self.next_btn)
        
        self.layout.add_widget(button_container)

        # Progress bar with proper styling
        self.progress = ProgressBar(
            max=100,
            size_hint=(1, None),
            height=30
        )
        self.layout.add_widget(self.progress)

        # Output label with proper styling
        self.output_label = Label(
            text="Ready",
            size_hint=(1, None),
            height=40,
            font_size=20,
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.output_label)

    def browse_directory(self, text_input):
        # Hide the main window temporarily
        root = tk.Tk()
        root.withdraw()
        
        # Open directory dialog
        directory = filedialog.askdirectory(
            title="Select Storage Directory",
            initialdir=os.path.expanduser("~")
        )
        
        # Update the text input if a directory was selected
        if directory:
            text_input.text = directory
        
        # Destroy the temporary window
        root.destroy()

    def next_screen(self, instance):
        self.manager.current = "vm"


# VM Properties screen
class VMScreen(Screen):
    def __init__(self, **kwargs):
        super(VMScreen, self).__init__(**kwargs)
        
        # Main container with padding
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        self.add_widget(self.layout)

        # Title
        title = Label(
            text="Configure Virtual Machine",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint=(1, None),
            height=50
        )
        self.layout.add_widget(title)

        # Form container with proper spacing
        self.form = GridLayout(
            cols=2,
            spacing=20,
            padding=20,
            size_hint=(1, None),
            height=300
        )
        
        # Add form elements with proper spacing
        form_elements = [
            ("RAM (GB):", "2", "text"),
            ("CPU Cores:", "2", "text"),
            ("ISO File:", "", "text")
        ]
        
        for label_text, default_value, input_type in form_elements:
            # Label
            label = Label(
                text=label_text,
                font_size=20,
                color=(1, 1, 1, 1),
                size_hint=(0.4, None),
                height=40
            )
            self.form.add_widget(label)
            
            # Input field container for ISO file
            if label_text == "ISO File:":
                input_container = BoxLayout(orientation="horizontal", spacing=10, size_hint=(0.6, None), height=40)
                
                # Text input
                input_field = TextInput(
                    text=default_value,
                    multiline=False,
                    font_size=20,
                    size_hint=(0.7, 1),
                    background_color=(0.2, 0.2, 0.2, 1),
                    foreground_color=(1, 1, 1, 1)
                )
                
                # Browse button
                browse_btn = Button(
                    text="Browse",
                    size_hint=(0.3, 1),
                    background_color=(0.3, 0.7, 1, 1),
                    font_size=16
                )
                browse_btn.bind(on_press=lambda x: self.browse_iso(input_field))
                
                input_container.add_widget(input_field)
                input_container.add_widget(browse_btn)
                self.form.add_widget(input_container)
                self.iso_input = input_field
            else:
                # Regular input field
                input_field = TextInput(
                    text=default_value,
                    multiline=False,
                    font_size=20,
                    size_hint=(0.6, None),
                    height=40,
                    background_color=(0.2, 0.2, 0.2, 1),
                    foreground_color=(1, 1, 1, 1)
                )
                self.form.add_widget(input_field)
            
            # Store reference to input field
            if label_text == "RAM (GB):":
                self.ram_input = input_field
            elif label_text == "CPU Cores:":
                self.cpu_input = input_field

        # Add form to scroll view
        scroll = ScrollView(
            size_hint=(1, 0.7),
            do_scroll_x=False
        )
        scroll.add_widget(self.form)
        self.layout.add_widget(scroll)

        # Button container
        button_container = BoxLayout(orientation="horizontal", spacing=20, size_hint=(1, None), height=60)
        
        # Back button
        self.back_btn = Button(
            text="Back",
            size_hint=(0.5, 1),
            background_color=(0.3, 0.7, 1, 1),
            font_size=24
        )
        self.back_btn.bind(on_press=self.prev_screen)
        button_container.add_widget(self.back_btn)

        # Create VM button
        self.create_btn = Button(
            text="Create VM",
            size_hint=(0.5, 1),
            background_color=(0.3, 0.7, 1, 1),
            font_size=24
        )
        self.create_btn.bind(on_press=self.create_vm)
        button_container.add_widget(self.create_btn)
        
        self.layout.add_widget(button_container)

        # Progress bar with proper styling
        self.progress = ProgressBar(
            max=100,
            size_hint=(1, None),
            height=30
        )
        self.layout.add_widget(self.progress)

        # Output label with proper styling
        self.output_label = Label(
            text="Ready",
            size_hint=(1, None),
            height=40,
            font_size=20,
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.output_label)

    def prev_screen(self, instance):
        self.manager.current = "disk"

    def browse_iso(self, text_input):
        # Hide the main window temporarily
        root = tk.Tk()
        root.withdraw()
        
        # Open file dialog for ISO selection
        file_path = filedialog.askopenfilename(
            title="Select ISO File",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        # Update the text input if a file was selected
        if file_path:
            text_input.text = file_path
        
        # Destroy the temporary window
        root.destroy()

    def create_vm(self, instance):
        try:
            ram = int(self.ram_input.text)
            cpu = int(self.cpu_input.text)
        except:
            self.output_label.text = "Invalid input values."
            return

        iso_path = self.iso_input.text
        
        # Get disk parameters from the disk screen
        disk_screen = self.manager.get_screen('disk')
        try:
            disk_size = int(disk_screen.disk_input.text)
        except:
            self.output_label.text = "Invalid disk size."
            return

        disk_format = disk_screen.disk_format_input.text
        storage_path = disk_screen.storage_input.text
        disk_name = disk_screen.disk_name_input.text

        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

        disk_path = os.path.join(storage_path, f"{disk_name}.{disk_format}")

        threading.Thread(
            target=self.create_vm_thread, args=(disk_size, disk_format, disk_path, ram, cpu, iso_path)
        ).start()

    def create_vm_thread(self, disk_size, disk_format, disk_path, ram, cpu, iso_path):
        self.progress.value = 10
        
        # Create disk
        cmd = ["qemu-img", "create", "-f", disk_format, disk_path, f"{disk_size}G"]
        subprocess.run(cmd)
        
        self.progress.value = 50
        
        # Create batch file for VM
        bat_path = disk_path.replace(os.path.splitext(disk_path)[1], ".bat")

        with open(bat_path, "w") as f:
            f.write("@echo off\n")
            if iso_path:
                f.write(
                    f'start "" C:\\msys64\\mingw64.exe qemu-system-x86_64 -hda "{disk_path}" -cdrom "{iso_path}" -boot d -m {ram*1024} -smp {cpu}\n'
                )
            else:
                f.write(
                    f'start "" C:\\msys64\\mingw64.exe qemu-system-x86_64 -hda "{disk_path}" -boot d -m {ram*1024} -smp {cpu}\n'
                )

        subprocess.Popen(
            ["cmd", "/c", bat_path], creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        self.progress.value = 100
        self.output_label.text = "VM Created and Started Successfully!"


# Main App
class CloudApp(App):
    def build(self):
        Config.set('kivy', 'keyboard_mode', 'system')
        Config.set('kivy', 'keyboard_layout', 'qwerty')
        Config.set('kivy', 'keyboard_type', 'text')
        
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(IntroScreen(name="intro"))
        sm.add_widget(DiskScreen(name="disk"))
        sm.add_widget(VMScreen(name="vm"))
        return sm


if __name__ == "__main__":
    CloudApp().run()
