from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle

from kivy.clock import Clock
from kivy.config import Config
import math
import os



# === Import your screens and utils ===
from vm_utils import (
    find_msys64,
    ServiceSelectionScreen,
    VMSelectionScreen,
    DiskScreen,
    DiskManagementScreen,
    VMScreen,
    ExistingVMsScreen,
)
from docker_utils import (
    DockerScreen,
    DockerImagesScreen,
    DockerContainersScreen,
)


# === 3D Cube Widget ===
class Rotating3DBox(Widget):
    def __init__(self, **kwargs):
        super(Rotating3DBox, self).__init__(**kwargs)
        self.angle = 0
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        Clock.schedule_interval(self.animate, 1 / 60.0)

    def project(self, x, y, z, fov, viewer_distance):
        factor = fov / (viewer_distance + z)
        x = x * factor + self.center_x
        y = -y * factor + self.center_y
        return x, y

    def update_graphics(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.0, 0.0, 0.0, 1)
            Rectangle(pos=self.pos, size=self.size)
            Color(0.0, 1.0, 0.0, 1)

            size = min(self.width, self.height) * 0.25
            vertices = [
                [-size, -size, -size],
                [size, -size, -size],
                [size, size, -size],
                [-size, size, -size],
                [-size, -size, size],
                [size, -size, size],
                [size, size, size],
                [-size, size, size],
            ]

            angle_x = math.radians(self.angle)
            angle_y = math.radians(self.angle)
            angle_z = math.radians(self.angle)

            def rotate(x, y, z):
                y, z = y * math.cos(angle_x) - z * math.sin(angle_x), y * math.sin(angle_x) + z * math.cos(angle_x)
                x, z = x * math.cos(angle_y) + z * math.sin(angle_y), -x * math.sin(angle_y) + z * math.cos(angle_y)
                x, y = x * math.cos(angle_z) - y * math.sin(angle_z), x * math.sin(angle_z) + y * math.cos(angle_z)
                return x, y, z

            projected = [self.project(*rotate(x, y, z), fov=256, viewer_distance=4 * size) for x, y, z in vertices]

            edges = [
                (0, 1), (1, 2), (2, 3), (3, 0),
                (4, 5), (5, 6), (6, 7), (7, 4),
                (0, 4), (1, 5), (2, 6), (3, 7),
            ]
            for edge in edges:
                Line(points=[*projected[edge[0]], *projected[edge[1]]], width=2)

    def animate(self, dt):
        self.angle += 1
        self.update_graphics()


# === Intro Screen with 3D Cube ===
class IntroScreen(Screen):
    def on_enter(self):
        layout = BoxLayout(orientation="vertical", padding=50)
        with layout.canvas.before:
            Color(0.0, 0.0, 0.0, 1)
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
            pos_hint={"center_x": 0.5},
        )
        self.start_btn.bind(on_press=self.start_app)
        layout.add_widget(self.start_btn)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def start_app(self, instance):
        self.manager.current = "service_selection"


# === Main App Class ===
class CloudApp(App):
    def build(self):
        Config.set("kivy", "keyboard_mode", "system")
        Config.set("kivy", "keyboard_layout", "qwerty")
        Config.set("kivy", "keyboard_type", "text")

        # Check for MSYS64 before proceeding
        msys_path = find_msys64()
        if msys_path is None:
            popup = Popup(
                title="Error",
                content=Label(text="MSYS64 not found in PATH. Please install MSYS64 and add it to your PATH environment variable."),
                size_hint=(None, None),
                size=(400, 200),
            )
            popup.open()
            return None

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(IntroScreen(name="intro"))
        sm.add_widget(ServiceSelectionScreen(name="service_selection"))
        sm.add_widget(VMSelectionScreen(name="vm_selection"))
        sm.add_widget(DiskScreen(name="disk"))
        sm.add_widget(DiskManagementScreen(name="manage_disks"))
        sm.add_widget(VMScreen(name="vm"))
        sm.add_widget(ExistingVMsScreen(name="existing_vms"))
        sm.add_widget(DockerScreen(name="docker"))
        sm.add_widget(DockerImagesScreen(name="docker_images"))
        sm.add_widget(DockerContainersScreen(name="docker_containers"))

        return sm


if __name__ == "__main__":
    CloudApp().run()