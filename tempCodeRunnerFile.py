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
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.properties import NumericProperty
import random
import math
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup


# Cloud widget - a collection of animated circles that simulate a 3D cloud
class CloudWidget(Widget):
    scale = NumericProperty(1.0)
    rotation = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(CloudWidget, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (400, 200)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
        self.clouds = []
        self.layers = 3  # Multiple layers for 3D effect
        
        # Schedule a delay to make sure widget size is set
        Clock.schedule_once(self._create_clouds, 0.1)
        
    def _create_clouds(self, dt):
        # Clear any previous clouds
        self.canvas.clear()
        self.clouds = []
        
        # Create cloud parts in multiple layers for 3D effect
        with self.canvas:
            # Create layers of clouds for 3D effect
            for layer in range(self.layers):
                layer_clouds = []
                
                # Layer background (different color for each layer)
                layer_alpha = 0.2 - 0.05 * layer  # Deeper layers are more transparent
                Color(0.7, 0.8, 1, layer_alpha)
                layer_bg = Ellipse(pos=(self.x, self.y), size=(self.width, self.height))
                
                # Create cloud puffs for this layer
                for _ in range(10):  # Fewer puffs per layer for better visuals
                    # Calculate positions with layer offset for 3D look
                    offset = 10 * layer
                    x = self.x + random.randint(offset, int(self.width) - 50 - offset)
                    y = self.y + random.randint(offset, int(self.height) - 50 - offset)
                    size = random.randint(60, 120)
                    
                    # Colors vary by layer - deeper layers are darker
                    r = g = b = 1.0 - (layer * 0.1)
                    Color(r, g, b, 0.8 - (layer * 0.2))
                    
                    cloud = Ellipse(pos=(x, y), size=(size, size))
                    layer_clouds.append((cloud, layer))
                
                self.clouds.extend(layer_clouds)
        
        # Start animation
        Clock.schedule_interval(self.update_cloud, 1/30)
    
    def update_cloud(self, dt):
        # Update rotation
        self.rotation += 0.5
        if self.rotation >= 360:
            self.rotation = 0
            
        # Calculate rotation center
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        
        # Move cloud parts to simulate 3D movement and rotation
        for cloud, layer in self.clouds:
            # Get the original position of the cloud relative to center
            orig_x, orig_y = cloud.pos
            rel_x = orig_x - cx
            rel_y = orig_y - cy
            
            # Calculate rotation around center (more pronounced for outer layers)
            rot_angle = math.radians(self.rotation / (layer + 1))
            new_rel_x = rel_x * math.cos(rot_angle) - rel_y * math.sin(rot_angle)
            new_rel_y = rel_x * math.sin(rot_angle) + rel_y * math.cos(rot_angle)
            
            # Add circular movement offset
            wiggle_x = math.sin(Clock.get_time() * 0.7 + layer) * 1.5
            wiggle_y = math.cos(Clock.get_time() * 0.5 + layer) * 1.2
            
            # Set new position
            cloud.pos = (cx + new_rel_x + wiggle_x, cy + new_rel_y + wiggle_y)
            
            # Scale based on rotation for 3D effect
            scale_pulse = 1.0 + 0.1 * math.sin(Clock.get_time() * 0.3 + layer)
            base_scale = 1.0 - 0.1 * layer  # Outer layers smaller
            total_scale = base_scale * scale_pulse
            
            orig_size = 80 + 10 * (layer % 3)
            cloud.size = (orig_size * total_scale, orig_size * total_scale)


# Intro screen
class IntroScreen(Screen):
    def on_enter(self):
        # Use a FloatLayout as the root to allow absolute positioning
        root_layout = FloatLayout()
        self.add_widget(root_layout)
        
        # Add the cloud widget first so it's behind other elements
        self.cloud = CloudWidget()
        root_layout.add_widget(self.cloud)
        
        # Main content in a BoxLayout
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=50)
        self.layout.opacity = 0  # Start hidden
        root_layout.add_widget(self.layout)
        
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
        
        # Spacer to push content up
        self.layout.add_widget(Widget(size_hint_y=0.2))
        
        # Start button - in center of screen
        button_layout = BoxLayout(size_hint=(1, None), height=50)
        # Left spacer
        button_layout.add_widget(Widget(size_hint_x=0.25))
        
        # Center button
        self.start_btn = Button(
            text="Start",
            size_hint_x=0.5,
            height=50,
            background_color=(0.3, 0.7, 1, 1),
            font_size=20,
            bold=True
        )
        self.start_btn.opacity = 0
        self.start_btn.bind(on_press=self.start_app)
        button_layout.add_widget(self.start_btn)
        
        # Right spacer
        button_layout.add_widget(Widget(size_hint_x=0.25))
        
        self.layout.add_widget(button_layout)
        
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
        # Clean transition to VM screen
        # First fade out current content
        anim = Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=self._switch_to_vm)
        anim.start(self.layout)
        
    def _switch_to_vm(self, *args):
        # Remove cloud widget and clear before transitioning
        if hasattr(self, 'cloud'):
            self.remove_widget(self.cloud)
        self.manager.current = "vm"


# VM Creation screen
class VMScreen(Screen):
    def __init__(self, **kwargs):
        super(VMScreen, self).__init__(**kwargs)
        
    def on_enter(self):
        # Clear any previous content
        self.clear_widgets()
        
        # Create the main layout
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        self.add_widget(self.layout)
        
        # Add a title
        title = Label(
            text="Virtual Machine Creator",
            font_size=24,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint_y=None,
            height=50
        )
        self.layout.add_widget(title)
        
        # Create scrollable form
        form_container = ScrollView(size_hint=(1, None), size=(800, 300))
        self.form = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.form.bind(minimum_height=self.form.setter("height"))
        
        # RAM
        self.form.add_widget(Label(text="RAM (GB):", size_hint_y=None, height=40))
        self.ram_input = TextInput(text="2", size_hint_y=None, height=40)
        self.form.add_widget(self.ram_input)
        
        # CPU
        self.form.add_widget(Label(text="CPU Cores:", size_hint_y=None, height=40))
        self.cpu_input = TextInput(text="2", size_hint_y=None, height=40)
        self.form.add_widget(self.cpu_input)
        
        # Disk Size
        self.form.add_widget(Label(text="Disk Size (GB):", size_hint_y=None, height=40))
        self.disk_input = TextInput(text="10", size_hint_y=None, height=40)
        self.form.add_widget(self.disk_input)
        
        # Disk Format
        self.form.add_widget(Label(text="Disk Format:", size_hint_y=None, height=40))
        self.disk_format_input = TextInput(text="qcow2", size_hint_y=None, height=40)
        self.form.add_widget(self.disk_format_input)
        
        # Storage Path
        self.form.add_widget(Label(text="Storage Path:", size_hint_y=None, height=40))
        path_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
        self.storage_input = TextInput(text=os.path.expanduser("~/vm_disks"))
        path_layout.add_widget(self.storage_input)
        
        # Add browse button
        browse_btn = Button(text="Browse", size_hint_x=0.3)
        browse_btn.bind(on_press=self.browse_path)
        path_layout.add_widget(browse_btn)
        self.form.add_widget(path_layout)
        
        # Disk Name
        self.form.add_widget(Label(text="Disk Name:", size_hint_y=None, height=40))
        self.disk_name_input = TextInput(text="vm_disk", size_hint_y=None, height=40)
        self.form.add_widget(self.disk_name_input)
        
        form_container.add_widget(self.form)
        self.layout.add_widget(form_container)
        
        # Add create button with some padding
        button_container = BoxLayout(size_hint_y=None, height=70, padding=[0, 10, 0, 0])
        self.create_btn = Button(
            text="Create VM",
            size_hint=(0.5, None),
            height=50,
            background_color=(0.3, 0.7, 1, 1),
            pos_hint={'center_x': 0.5}
        )
        self.create_btn.bind(on_press=self.create_vm)
        button_container.add_widget(self.create_btn)
        self.layout.add_widget(button_container)
        
        # Progress bar
        progress_container = BoxLayout(orientation="vertical", size_hint_y=None, height=80)
        self.progress = ProgressBar(max=100, size_hint=(1, None), height=20)
        progress_container.add_widget(self.progress)
        
        # Status output
        self.output_label = Label(
            text="Ready to create VM",
            size_hint=(1, None),
            height=50,
            halign='center',
            valign='middle'
        )
        self.output_label.bind(size=self.output_label.setter('text_size'))
        progress_container.add_widget(self.output_label)
        self.layout.add_widget(progress_container)
    
    def browse_path(self, instance):
        """Open a directory selection dialog when the browse button is clicked"""
        # Create content for the popup
        content = BoxLayout(orientation='vertical')
        
        # For Windows, start at the root level to show drives
        import platform
        if platform.system() == 'Windows':
            start_path = 'C:\\'  # Start at C: drive
        else:
            start_path = os.path.expanduser('~')
        
        # Add a button to navigate to root/drives
        drives_layout = BoxLayout(size_hint_y=None, height=40)
        drives_label = Label(text="Drives:", size_hint_x=0.3)
        drives_layout.add_widget(drives_label)
        
        # Add buttons for common drives
        for drive in ['C:', 'D:', 'E:', 'F:']:
            if os.path.exists(f"{drive}\\"):
                drive_btn = Button(text=drive)
                drive_btn.drive = drive  # Store the drive letter
                drives_layout.add_widget(drive_btn)
        
        # Create a file chooser that only allows directory selection
        file_chooser = FileChooserListView(path=start_path, dirselect=True)
        
        # Create buttons for the popup
        btn_layout = BoxLayout(size_hint_y=None, height=50)
        btn_cancel = Button(text='Cancel')
        btn_select = Button(text='Select')
        
        # Add buttons to layout
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_select)
        
        # Add all components to content
        content.add_widget(drives_layout)
        content.add_widget(file_chooser)
        content.add_widget(btn_layout)
        
        # Create popup
        popup = Popup(title='Select Directory', content=content, size_hint=(0.9, 0.9))
        
        # Function to navigate to a drive when clicked
        def go_to_drive(instance):
            file_chooser.path = f"{instance.drive}\\"
        
        # Bind drive buttons
        for child in drives_layout.children:
            if isinstance(child, Button):
                child.bind(on_release=go_to_drive)
        
        # Bind the buttons to actions
        btn_cancel.bind(on_release=popup.dismiss)
        
        # Update path when directory is selected
        def select_directory(instance):
            if file_chooser.path:
                self.storage_input.text = file_chooser.path
            popup.dismiss()
        
        btn_select.bind(on_release=select_directory)
        
        # Open the popup
        popup.open()
    
    def create_vm(self, instance):
        # Validate and launch in thread
        try:
            ram = int(self.ram_input.text)
            cpu = int(self.cpu_input.text)
            disk = int(self.disk_input.text)
            
            if ram <= 0 or cpu <= 0 or disk <= 0:
                self.output_label.text = "Values must be positive numbers"
                return
                
        except ValueError:
            self.output_label.text = "Invalid input. Please enter numbers only."
            return
        
        disk_format = self.disk_format_input.text
        storage_path = self.storage_input.text
        disk_name = self.disk_name_input.text
        
        if not disk_name:
            self.output_label.text = "Please enter a disk name"
            return
        
        if not os.path.exists(storage_path):
            try:
                os.makedirs(storage_path)
            except Exception as e:
                self.output_label.text = f"Error creating directory: {e}"
                return
        
        disk_path = os.path.join(storage_path, f"{disk_name}.{disk_format}")
        
        # Update UI before starting
        self.output_label.text = "Creating VM..."
        self.progress.value = 5
        
        # Start the process in a thread to keep UI responsive
        threading.Thread(
            target=self.create_vm_thread, 
            args=(disk, disk_format, disk_path, ram, cpu),
            daemon=True
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
