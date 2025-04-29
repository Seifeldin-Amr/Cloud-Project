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
from kivy.graphics import Color, Line, Rectangle
import os
import threading
import subprocess
import math

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
import os
import threading
import subprocess

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
        self.manager.current = "vm"

class VMScreen(Screen):
    def __init__(self, **kwargs):
        super(VMScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        self.add_widget(self.layout)

        self.form = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.form.bind(minimum_height=self.form.setter("height"))

        self.form.add_widget(Label(text="RAM (GB):"))
        self.ram_input = TextInput(text="2")
        self.form.add_widget(self.ram_input)

        self.form.add_widget(Label(text="CPU Cores:"))
        self.cpu_input = TextInput(text="2")
        self.form.add_widget(self.cpu_input)

        self.form.add_widget(Label(text="Disk Size (GB):"))
        self.disk_input = TextInput(text="10")
        self.form.add_widget(self.disk_input)

        self.form.add_widget(Label(text="Disk Format:"))
        self.disk_format_input = TextInput(text="qcow2")
        self.form.add_widget(self.disk_format_input)

        self.form.add_widget(Label(text="Storage Path:"))
        self.storage_input = TextInput(text=os.path.expanduser("~/vm_disks"))
        self.form.add_widget(self.storage_input)

        self.form.add_widget(Label(text="Disk Name:"))
        self.disk_name_input = TextInput(text="vm_disk")
        self.form.add_widget(self.disk_name_input)

        scroll = ScrollView(size_hint=(1, None), size=(800, 400))
        scroll.add_widget(self.form)

        self.layout.add_widget(scroll)

        self.create_btn = Button(
            text="Create VM",
            size_hint=(1, None),
            height=50,
            background_color=(0.3, 0.7, 1, 1),
        )
        self.create_btn.bind(on_press=self.create_vm)
        self.layout.add_widget(self.create_btn)

        self.progress = ProgressBar(max=100, size_hint=(1, None), height=20)
        self.layout.add_widget(self.progress)

        self.output_label = Label(text="Ready", size_hint=(1, None), height=50)
        self.layout.add_widget(self.output_label)

    def create_vm(self, instance):
        try:
            ram = int(self.ram_input.text)
            cpu = int(self.cpu_input.text)
            disk = int(self.disk_input.text)
        except:
            self.output_label.text = "Invalid input."
            return

        disk_format = self.disk_format_input.text
        storage_path = self.storage_input.text
        disk_name = self.disk_name_input.text

        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

        disk_path = os.path.join(storage_path, f"{disk_name}.{disk_format}")

        threading.Thread(
            target=self.create_vm_thread, args=(disk, disk_format, disk_path, ram, cpu)
        ).start()

    def create_vm_thread(self, disk_size, disk_format, disk_path, ram, cpu):
        self.progress.value = 10
        cmd = ["qemu-img", "create", "-f", disk_format, disk_path, f"{disk_size}G"]
        subprocess.run(cmd)
        self.progress.value = 40
        bat_path = disk_path.replace(f".{disk_format}", ".bat")

        with open(bat_path, "w") as f:
            f.write("@echo off\n")
            f.write(
                f'start "" C:\\msys64\\mingw64.exe qemu-system-x86_64 -hda "{disk_path}" -boot d -m {ram*1024} -smp {cpu}\n'
            )

        subprocess.Popen(
            ["cmd", "/c", bat_path], creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        self.progress.value = 100
        self.output_label.text = "VM Created and Started!"


class CloudApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(IntroScreen(name="intro"))
        sm.add_widget(VMScreen(name="vm"))
        return sm


if __name__ == "__main__":
    CloudApp().run()