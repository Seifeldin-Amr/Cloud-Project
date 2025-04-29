from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
import os
import threading
import subprocess


# Intro screen
class IntroScreen(Screen):
    def on_enter(self):
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=50)
        self.layout.opacity = 0  # Start hidden
        self.add_widget(self.layout)

        # Team names
        self.team_labels = [
            Label(text="Ahmed Abdelmoneim", font_size=24, color=(1, 1, 1, 1)),
            Label(text="Seifeldin Amr", font_size=24, color=(1, 1, 1, 1)),
            Label(text="Yahia Anas", font_size=24, color=(1, 1, 1, 1)),
        ]

        for lbl in self.team_labels:
            lbl.opacity = 0
            self.layout.add_widget(lbl)

        # Project title
        self.title_label = Label(
            text="Cloud Management System",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
        )
        self.title_label.opacity = 0
        self.layout.add_widget(self.title_label)

        # Start button
        self.start_btn = Button(
            text="Start",
            size_hint=(0.5, None),
            height=50,
            background_color=(0.3, 0.7, 1, 1),
        )
        self.start_btn.opacity = 0
        self.start_btn.bind(on_press=self.start_app)
        self.layout.add_widget(self.start_btn)

        # Start animation sequence
        Clock.schedule_once(self.start_animation, 0.5)

    def start_animation(self, *args):
        # Fade in the whole layout
        anim = Animation(opacity=1, duration=0.5)
        anim.start(self.layout)

        # Animate team names one after another
        delay = 0
        for lbl in self.team_labels:
            Clock.schedule_once(
                lambda dt, l=lbl: Animation(opacity=1, duration=0.5).start(l), delay
            )
            delay += 0.5

        # Animate title
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.7).start(self.title_label), delay
        )
        delay += 0.7

        # Animate start button
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.5).start(self.start_btn), delay
        )

    def start_app(self, instance):
        self.manager.current = "vm"


# VM Creation screen
class VMScreen(Screen):
    def __init__(self, **kwargs):
        super(VMScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        self.add_widget(self.layout)

        self.form = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.form.bind(minimum_height=self.form.setter("height"))

        # RAM
        self.form.add_widget(Label(text="RAM (GB):"))
        self.ram_input = TextInput(text="2")
        self.form.add_widget(self.ram_input)

        # CPU
        self.form.add_widget(Label(text="CPU Cores:"))
        self.cpu_input = TextInput(text="2")
        self.form.add_widget(self.cpu_input)

        # Disk Size
        self.form.add_widget(Label(text="Disk Size (GB):"))
        self.disk_input = TextInput(text="10")
        self.form.add_widget(self.disk_input)

        # Disk Format
        self.form.add_widget(Label(text="Disk Format:"))
        self.disk_format_input = TextInput(text="qcow2")
        self.form.add_widget(self.disk_format_input)

        # Storage Path
        self.form.add_widget(Label(text="Storage Path:"))
        self.storage_input = TextInput(text=os.path.expanduser("~/vm_disks"))
        self.form.add_widget(self.storage_input)

        # Disk Name
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
        # Validate and launch in thread
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


# Main App
class CloudApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(IntroScreen(name="intro"))
        sm.add_widget(VMScreen(name="vm"))
        return sm


if __name__ == "__main__":
    CloudApp().run()
