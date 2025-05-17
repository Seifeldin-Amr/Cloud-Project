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
from kivy.uix.popup import Popup

# Import Docker for Python SDK
try:
    import docker

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


def find_msys64():
    # Check PATH environment variable
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for path in path_dirs:
        # Check for both MSYS2 and msys64 in the path
        if "msys2" in path.lower() or "msys64" in path.lower():
            # Try to find the base MSYS2 directory
            path_parts = path.split(os.sep)
            for i, part in enumerate(path_parts):
                if part.lower() in ["msys2", "msys64"]:
                    # Reconstruct the base path
                    base_path = os.sep.join(path_parts[: i + 1])
                    if os.path.exists(base_path):
                        return base_path

                    # Also check one level up (in case we're in a subdirectory)
                    parent_path = os.path.dirname(base_path)
                    if os.path.exists(parent_path):
                        return parent_path

    # Check common installation paths
    common_paths = [
        "C:\\msys64",
        "D:\\msys64",
        "C:\\Program Files\\MSYS2",
        "D:\\Program Files\\MSYS2",
        os.path.expanduser("~\\msys64"),
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    return None


def get_disk_directory():
    msys_path = find_msys64()
    if not msys_path:
        return None

    # Get the username and create the disk directory path
    username = os.getlogin()
    disk_dir = os.path.join(msys_path, "home", username, "qemu-disks")

    # Create the directory if it doesn't exist
    try:
        os.makedirs(disk_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating disk directory: {str(e)}")
        return None

    return disk_dir


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
            Color(0.0, 0.0, 0.0, 1)  # Set full black background
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
                y, z = y * math.cos(angle_x) - z * math.sin(angle_x), y * math.sin(
                    angle_x
                ) + z * math.cos(angle_x)
                x, z = x * math.cos(angle_y) + z * math.sin(angle_y), -x * math.sin(
                    angle_y
                ) + z * math.cos(angle_y)
                x, y = x * math.cos(angle_z) - y * math.sin(angle_z), x * math.sin(
                    angle_z
                ) + y * math.cos(angle_z)
                return x, y, z

            projected = [
                self.project(*rotate(x, y, z), fov=256, viewer_distance=4 * size)
                for x, y, z in vertices
            ]

            edges = [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 0),
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 4),
                (0, 4),
                (1, 5),
                (2, 6),
                (3, 7),
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
            pos_hint={"center_x": 0.5},
        )
        self.start_btn.bind(on_press=self.start_app)
        layout.add_widget(self.start_btn)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def start_app(self, instance):
        self.manager.current = "service_selection"


class ServiceSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(ServiceSelectionScreen, self).__init__(**kwargs)

        # Main container with padding
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        self.add_widget(self.layout)

        # Title
        title = Label(
            text="Cloud Management System",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint=(1, None),
            height=50,
        )
        self.layout.add_widget(title)

        # Button container
        button_container = BoxLayout(
            orientation="vertical", spacing=30, size_hint=(1, 0.6)
        )

        # VM Management button
        self.vm_management_btn = Button(
            text="Virtual Machine Management",
            size_hint=(0.8, None),
            height=80,
            background_color=(0.3, 0.7, 1, 1),
            font_size=28,
            pos_hint={"center_x": 0.5},
        )
        self.vm_management_btn.bind(on_press=self.go_to_vm_management)
        button_container.add_widget(self.vm_management_btn)

        # Docker Management button
        self.docker_management_btn = Button(
            text="Docker Management",
            size_hint=(0.8, None),
            height=80,
            background_color=(0.3, 0.7, 1, 1),
            font_size=28,
            pos_hint={"center_x": 0.5},
        )
        self.docker_management_btn.bind(on_press=self.go_to_docker_management)
        button_container.add_widget(self.docker_management_btn)

        self.layout.add_widget(button_container)

    def go_to_vm_management(self, instance):
        self.manager.current = "vm_selection"

    def go_to_docker_management(self, instance):
        self.manager.current = "docker"


class VMSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(VMSelectionScreen, self).__init__(**kwargs)

        # Main container with padding
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        self.add_widget(self.layout)

        # Title
        title = Label(
            text="Virtual Machine Manager",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint=(1, None),
            height=50,
        )
        self.layout.add_widget(title)

        # Button container
        button_container = BoxLayout(
            orientation="vertical", spacing=20, size_hint=(1, 0.6)
        )

        # Create Disk button
        self.create_disk_btn = Button(
            text="Create Virtual Disk",
            size_hint=(0.8, None),
            height=60,
            background_color=(0.3, 0.7, 1, 1),
            font_size=24,
            pos_hint={"center_x": 0.5},
        )
        self.create_disk_btn.bind(on_press=self.go_to_disk)
        button_container.add_widget(self.create_disk_btn)

        # Manage Disks button
        self.manage_disks_btn = Button(
            text="Manage Virtual Disks",
            size_hint=(0.8, None),
            height=60,
            background_color=(0.3, 0.7, 1, 1),
            font_size=24,
            pos_hint={"center_x": 0.5},
        )
        self.manage_disks_btn.bind(on_press=self.go_to_manage_disks)
        button_container.add_widget(self.manage_disks_btn)

        # Create VM button
        self.create_vm_btn = Button(
            text="Create Virtual Machine",
            size_hint=(0.8, None),
            height=60,
            background_color=(0.3, 0.7, 1, 1),
            font_size=24,
            pos_hint={"center_x": 0.5},
        )
        self.create_vm_btn.bind(on_press=self.go_to_vm)
        button_container.add_widget(self.create_vm_btn)

        # Access Existing VMs button
        self.access_vm_btn = Button(
            text="Access Existing VMs",
            size_hint=(0.8, None),
            height=60,
            background_color=(0.3, 0.7, 1, 1),
            font_size=24,
            pos_hint={"center_x": 0.5},
        )
        self.access_vm_btn.bind(on_press=self.go_to_existing_vms)
        button_container.add_widget(self.access_vm_btn)

        self.layout.add_widget(button_container)

        # Back button
        self.back_btn = Button(
            text="Back to Main Menu",
            size_hint=(0.4, None),
            height=50,
            background_color=(0.3, 0.7, 1, 1),
            pos_hint={"center_x": 0.5},
        )
        self.back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_btn)

    def go_to_disk(self, instance):
        self.manager.current = "disk"

    def go_to_manage_disks(self, instance):
        self.manager.current = "manage_disks"

    def go_to_vm(self, instance):
        self.manager.current = "vm"

    def go_to_existing_vms(self, instance):
        self.manager.current = "existing_vms"

    def go_back(self, instance):
        self.manager.current = "service_selection"


class DockerScreen(Screen):
    def __init__(self, **kwargs):
        super(DockerScreen, self).__init__(**kwargs)

        # Initialize Docker client
        try:
            import docker

            self.docker_client = docker.from_env()
            self.docker_available = True
        except Exception as e:
            self.docker_client = None
            self.docker_available = False

        # Main container with padding
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        self.add_widget(self.layout)

        # Title
        title = Label(
            text="Docker Management",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint=(1, None),
            height=50,
        )
        self.layout.add_widget(title)

        # Button container
        button_container = BoxLayout(
            orientation="vertical", spacing=20, size_hint=(1, 0.6)
        )

        # Create Dockerfile button
        self.create_dockerfile_btn = Button(
            text="Create Dockerfile",
            size_hint=(0.8, None),
            height=60,
            background_color=(0.3, 0.7, 1, 1),
            font_size=24,
            pos_hint={"center_x": 0.5},
        )
        self.create_dockerfile_btn.bind(on_press=self.create_dockerfile)
        button_container.add_widget(self.create_dockerfile_btn)

        # Build Docker Image button
        self.build_image_btn = Button(
            text="Build Docker Image",
            size_hint=(0.8, None),
            height=60,
            background_color=(0.3, 0.7, 1, 1),
            font_size=24,
            pos_hint={"center_x": 0.5},
        )
        self.build_image_btn.bind(on_press=self.build_docker_image)
        button_container.add_widget(self.build_image_btn)

        # Manage Docker Images button
        self.manage_images_btn = Button(
            text="Manage Docker Images",
            size_hint=(0.8, None),
            height=60,
            background_color=(0.3, 0.7, 1, 1),
            font_size=24,
            pos_hint={"center_x": 0.5},
        )
        self.manage_images_btn.bind(on_press=self.go_to_images)
        button_container.add_widget(self.manage_images_btn)

        # Manage Docker Containers button
        self.manage_containers_btn = Button(
            text="Manage Docker Containers",
            size_hint=(0.8, None),
            height=60,
            background_color=(0.3, 0.7, 1, 1),
            font_size=24,
            pos_hint={"center_x": 0.5},
        )
        self.manage_containers_btn.bind(on_press=self.go_to_containers)
        button_container.add_widget(self.manage_containers_btn)

        # Pull Docker Image button
        self.pull_image_btn = Button(
            text="Pull Docker Image",
            size_hint=(0.8, None),
            height=60,
            background_color=(0.3, 0.7, 1, 1),
            font_size=24,
            pos_hint={"center_x": 0.5},
        )
        self.pull_image_btn.bind(on_press=self.pull_image)
        button_container.add_widget(self.pull_image_btn)

        self.layout.add_widget(button_container)

        # Back button
        self.back_btn = Button(
            text="Back to Main Menu",
            size_hint=(0.3, None),
            height=50,
            background_color=(0.3, 0.7, 1, 1),
            pos_hint={"center_x": 0.5},
        )
        self.back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_btn)

    def create_dockerfile(self, instance):
        """Create a Dockerfile with user-specified content"""
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Instructions label
        layout.add_widget(
            Label(text="Enter Dockerfile content:", size_hint_y=None, height=30)
        )

        # Text input for Dockerfile content with default template
        default_content = """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .          
CMD ["python", "app.py"]
"""
        text_input = TextInput(text=default_content, multiline=True, size_hint=(1, 1))
        layout.add_widget(text_input)

        # Path input
        path_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        path_layout.add_widget(Label(text="Save to directory:", size_hint_x=0.3))
        path_input = TextInput(text=os.getcwd(), size_hint_x=0.7)
        path_layout.add_widget(path_input)
        layout.add_widget(path_layout)

        # Button layout
        btn_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50, spacing=10
        )

        # Function to save Dockerfile
        def save_dockerfile(btn):
            try:
                dockerfile_path = os.path.join(path_input.text, "Dockerfile")
                with open(dockerfile_path, "w") as f:
                    f.write(text_input.text)
                result_popup = Popup(
                    title="Success",
                    content=Label(text=f"Dockerfile saved to {dockerfile_path}"),
                    size_hint=(0.6, 0.3),
                )
                result_popup.open()
                popup.dismiss()
            except Exception as e:
                error_popup = Popup(
                    title="Error",
                    content=Label(text=f"Failed to save Dockerfile: {str(e)}"),
                    size_hint=(0.6, 0.3),
                )
                error_popup.open()

        # Create save and cancel buttons
        save_btn = Button(text="Save")
        save_btn.bind(on_press=save_dockerfile)
        cancel_btn = Button(text="Cancel")
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)

        # Create and open popup
        popup = Popup(title="Create Dockerfile", content=layout, size_hint=(0.8, 0.8))
        popup.open()

    def build_docker_image(self, instance):
        """Build a Docker image using the Python Docker SDK"""
        if not self._check_docker_client():
            return

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Path input
        path_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        path_layout.add_widget(Label(text="Dockerfile directory:", size_hint_x=0.3))
        path_input = TextInput(text=os.getcwd(), size_hint_x=0.7)
        path_layout.add_widget(path_input)
        layout.add_widget(path_layout)

        # Image name input
        name_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        name_layout.add_widget(Label(text="Image name:tag:", size_hint_x=0.3))
        name_input = TextInput(text="my-app:latest", size_hint_x=0.7)
        name_layout.add_widget(name_input)
        layout.add_widget(name_layout)

        # Output display
        output_text = TextInput(readonly=True, multiline=True, size_hint=(1, 1))
        layout.add_widget(Label(text="Build output:", size_hint_y=None, height=30))
        layout.add_widget(output_text)

        # Button layout
        btn_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50, spacing=10
        )

        # Function to build Docker image
        def build_image(btn):
            try:
                path = path_input.text
                tag = name_input.text

                output_text.text = f"Building image {tag} from {path}...\n"

                # Use a thread to avoid UI freezing
                def build_thread():
                    try:
                        # Build Docker image with Python SDK
                        image, build_logs = self.docker_client.images.build(
                            path=path,
                            tag=tag,
                            rm=True,
                        )

                        # Log the output
                        log_output = "Build completed successfully!\n"
                        log_output += f"Created image: {image.tags[0]}\n"

                        # Update UI on main thread
                        Clock.schedule_once(
                            lambda dt: setattr(output_text, "text", log_output), 0
                        )
                    except Exception as e:
                        error_msg = f"Error building image: {str(e)}"
                        Clock.schedule_once(
                            lambda dt: setattr(output_text, "text", error_msg), 0
                        )

                threading.Thread(target=build_thread).start()

            except Exception as e:
                output_text.text = f"Error: {str(e)}"

        # Create build and cancel buttons
        build_btn = Button(text="Build")
        build_btn.bind(on_press=build_image)
        cancel_btn = Button(text="Close")
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        btn_layout.add_widget(build_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)

        # Create and open popup
        popup = Popup(title="Build Docker Image", content=layout, size_hint=(0.8, 0.8))
        popup.open()

    def pull_image(self, instance):
        """Pull a Docker image – now with Hub autocomplete"""
        if not self._check_docker_client():
            return

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # ---------------- top line: search box + status --------------------
        search_row = BoxLayout(size_hint_y=None, height=30, spacing=5)

        name_input = TextInput(
            hint_text="Type image name (e.g. nginx)…",
            multiline=False,
            size_hint_x=0.7,
        )
        status_lbl = Label(text="", size_hint_x=0.3)
        search_row.add_widget(name_input)
        search_row.add_widget(status_lbl)
        layout.add_widget(search_row)

        # ---------------- drop-down suggestions ---------------------------
        from kivy.uix.dropdown import DropDown
        dropdown = DropDown(auto_width=False)

        def show_dropdown(suggestions):
            dropdown.clear_widgets()
            for repo in suggestions:
                btn = Button(
                    text=repo,
                    size_hint_y=None,
                    height=34,
                    halign="left",
                    valign="middle",
                    background_color=(0.2, 0.6, 0.9, 1),
                )
                btn.bind(size=lambda b, *a: setattr(b, "text_size", b.size))
                btn.bind(on_release=lambda b: dropdown.select(b.text))
                dropdown.add_widget(btn)

            dropdown.width = max(200, name_input.width * 2)

            # ── guard ──────────────────────────────────────────────────────────
            if suggestions:
                # open only once; afterwards we just refresh its children
                if not dropdown.attach_to:          # attach_to is None until first open()
                    dropdown.open(name_input)
            else:
                dropdown.dismiss()



        # when a suggestion is picked, copy it into the TextInput
        dropdown.bind(on_select=lambda _, value: setattr(name_input, "text", value))

        # ---------------- results / log textbox ---------------------------
        output_text = TextInput(readonly=True, multiline=True, size_hint=(1, 1))
        layout.add_widget(Label(text="Pull output:", size_hint_y=None, height=30))
        layout.add_widget(output_text)

        # ---------------- buttons -----------------------------------------
        btn_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        pull_btn = Button(text="Pull")
        close_btn = Button(text="Close")
        btn_row.add_widget(pull_btn)
        btn_row.add_widget(close_btn)
        layout.add_widget(btn_row)

        popup = Popup(title="Pull Docker Image", content=layout, size_hint=(0.8, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

        # ==================================================================
        #  A) live-search every time user types ≥ 3 chars  (debounced)
        # ==================================================================
        from functools import partial
        import time
        last_req = {"term": "", "t": 0}

        def on_text_change(_inst, new_text):
            term = new_text.strip()
            if len(term) < 3 or term == last_req["term"]:
                return
            last_req["term"] = term
            last_req["t"] = time.time()
            status_lbl.text = "…"

            def search_thread(tsnapshot):
                try:
                    hits = self.docker_client.images.search(term, limit=5)
                    # ignore stale responses
                    if tsnapshot != last_req["t"]:
                        return
                    repos = [hit["name"] for hit in hits]        # list of strings
                    Clock.schedule_once(lambda dt: (
                        setattr(status_lbl, "text", f"{len(repos)}⧉" if repos else "0"),
                        show_dropdown(repos)
                    ), 0)
                except Exception as e:
                    print("SEARCH ERROR:", e)            # ← prints to your terminal
                    Clock.schedule_once(lambda dt: setattr(output_text, "text", f"{e}\n"))
                    Clock.schedule_once(lambda dt: setattr(status_lbl, "text", "Err"))


            threading.Thread(target=search_thread, args=(last_req["t"],), daemon=True).start()

        name_input.bind(text=on_text_change)

        # ==================================================================
        #  B) perform the actual pull
        # ==================================================================
        def do_pull(_btn):
            image_name = name_input.text.strip()
            if not image_name:
                output_text.text = "Please select or type an image name"
                return
            output_text.text = f"Pulling {image_name} …\n"
            pull_btn.disabled = True

            def pull_thread():
                try:
                    # download image (blocking call on this background thread)
                    self.docker_client.images.pull(image_name)

                    # UI update: show success message
                    Clock.schedule_once(
                        lambda dt: setattr(
                            output_text,
                            "text",
                            f"Successfully pulled {image_name}\n"
                        ),
                        0
                    )

                    # refresh the Images screen, if it’s already been created
                    Clock.schedule_once(
                        lambda dt: self.manager.get_screen("docker_images").update_image_list(),
                        0
                    )

                except Exception as e:
                    Clock.schedule_once(
                        lambda dt: setattr(
                            output_text,
                            "text",
                            f"Failed: {e}\n"
                        ),
                        0
                    )

                finally:
                    # re-enable the Pull button
                    Clock.schedule_once(
                        lambda dt: setattr(pull_btn, "disabled", False),
                        0
                    )

            threading.Thread(target=pull_thread, daemon=True).start()

        pull_btn.bind(on_press=do_pull)

    def go_to_images(self, instance):
        """Navigate to the Docker images management screen"""
        self.manager.current = "docker_images"

    def go_to_containers(self, instance):
        """Navigate to the Docker containers management screen"""
        self.manager.current = "docker_containers"

    def _check_docker_client(self):
        """Check if Docker client is available, show error if not"""
        if not self.docker_available:
            try:
                import docker

                self.docker_client = docker.from_env()
                self.docker_available = True
            except Exception as e:
                error_popup = Popup(
                    title="Docker Error",
                    content=Label(
                        text=f"Could not connect to Docker: {str(e)}\n\nPlease make sure Docker is installed and running."
                    ),
                    size_hint=(0.7, 0.3),
                )
                error_popup.open()
                return False
        return True

    def go_back(self, instance):
        self.manager.current = "service_selection"


class DockerImagesScreen(Screen):
    def __init__(self, **kwargs):
        super(DockerImagesScreen, self).__init__(**kwargs)

        # Try to initialize the Docker client
        try:
            self.docker_client = docker.from_env()
            self.docker_available = True
        except Exception as e:
            self.docker_client = None
            self.docker_available = False

        # Main container with padding
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        self.add_widget(self.layout)

        # Title and header
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=50)
        title = Label(
            text="Docker Images",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint=(0.7, 1),
        )
        header.add_widget(title)

        # Refresh button
        refresh_btn = Button(
            text="Refresh", size_hint=(0.3, 1), background_color=(0.3, 0.7, 1, 1)
        )
        refresh_btn.bind(on_press=lambda x: self.update_image_list())
        header.add_widget(refresh_btn)

        self.layout.add_widget(header)

        # Status label
        self.status_label = Label(text="", size_hint=(1, None), height=30)
        self.layout.add_widget(self.status_label)

        # Images list container
        images_container = BoxLayout(orientation="vertical", spacing=10)

        # Column headers
        headers = GridLayout(cols=4, size_hint_y=None, height=40, spacing=2)
        headers.add_widget(Label(text="Repository", bold=True))
        headers.add_widget(Label(text="Tag", bold=True))
        headers.add_widget(Label(text="Image ID", bold=True))
        headers.add_widget(Label(text="Actions", bold=True))
        images_container.add_widget(headers)

        # Scroll view for image list
        scroll = ScrollView()
        self.image_list = GridLayout(cols=4, spacing=2, size_hint_y=None)
        self.image_list.bind(minimum_height=self.image_list.setter("height"))
        scroll.add_widget(self.image_list)
        images_container.add_widget(scroll)

        self.layout.add_widget(images_container)

        # Button container
        button_container = BoxLayout(
            orientation="horizontal", spacing=20, size_hint=(1, None), height=50
        )

        # Pull Image button
        self.pull_btn = Button(
            text="Pull Image", size_hint=(0.5, 1), background_color=(0.3, 0.7, 1, 1)
        )
        self.pull_btn.bind(on_press=self.pull_image)
        button_container.add_widget(self.pull_btn)

        # Back button
        self.back_btn = Button(
            text="Back", size_hint=(0.5, 1), background_color=(0.3, 0.7, 1, 1)
        )
        self.back_btn.bind(on_press=self.go_back)
        button_container.add_widget(self.back_btn)

        self.layout.add_widget(button_container)

    def on_enter(self):
        self.update_image_list()

    def update_image_list(self):
        """Refresh the list of Docker images"""
        self.image_list.clear_widgets()

        if not self._check_docker_client():
            self.status_label.text = "Docker is not available"
            return

        try:
            # Change status
            self.status_label.text = "Loading Docker images..."

            # Get all Docker images
            images = self.docker_client.images.list()

            if not images:
                self.status_label.text = "No Docker images found"
                return

            # Add each image to the list
            for image in images:
                # Get image tags and ID
                if image.tags:
                    for tag in image.tags:
                        # Parse the repository and tag
                        if ":" in tag:
                            repo, tag_name = tag.split(":", 1)
                        else:
                            repo, tag_name = tag, "latest"

                        # Add the repository
                        self.image_list.add_widget(
                            Label(text=repo, size_hint_y=None, height=40)
                        )

                        # Add the tag
                        self.image_list.add_widget(
                            Label(text=tag_name, size_hint_y=None, height=40)
                        )

                        # Add the ID (shortened)
                        image_id = image.short_id.replace("sha256:", "")
                        self.image_list.add_widget(
                            Label(text=image_id, size_hint_y=None, height=40)
                        )

                        # Add action buttons
                        action_layout = BoxLayout(
                            orientation="horizontal",
                            spacing=5,
                            size_hint_y=None,
                            height=40,
                        )

                        # Run button
                        run_btn = Button(
                            text="Run",
                            size_hint_x=0.5,
                            background_color=(0.3, 0.7, 1, 1),
                        )
                        run_btn.bind(
                            on_press=lambda x, img=tag: self.run_container(img)
                        )
                        action_layout.add_widget(run_btn)

                        # Remove button
                        remove_btn = Button(
                            text="Remove",
                            size_hint_x=0.5,
                            background_color=(1, 0.3, 0.3, 1),
                        )
                        remove_btn.bind(
                            on_press=lambda x, img=tag: self.remove_image(img)
                        )
                        action_layout.add_widget(remove_btn)

                        self.image_list.add_widget(action_layout)
                else:
                    # Handle untagged images
                    self.image_list.add_widget(
                        Label(text="<none>", size_hint_y=None, height=40)
                    )

                    self.image_list.add_widget(
                        Label(text="<none>", size_hint_y=None, height=40)
                    )

                    # Add the ID (shortened)
                    image_id = image.short_id.replace("sha256:", "")
                    self.image_list.add_widget(
                        Label(text=image_id, size_hint_y=None, height=40)
                    )

                    # Add action buttons
                    action_layout = BoxLayout(
                        orientation="horizontal", spacing=5, size_hint_y=None, height=40
                    )

                    # Remove button only for untagged images
                    remove_btn = Button(
                        text="Remove",
                        size_hint_x=1.0,
                        background_color=(1, 0.3, 0.3, 1),
                    )
                    remove_btn.bind(
                        on_press=lambda x, img_id=image_id: self.remove_image_by_id(
                            img_id
                        )
                    )
                    action_layout.add_widget(remove_btn)

                    self.image_list.add_widget(action_layout)

            self.status_label.text = f"Found {len(images)} Docker images"

        except Exception as e:
            self.status_label.text = f"Error loading images: {str(e)}"

    def run_container(self, image_name):
        """Run a new container from the selected image"""
        if not self._check_docker_client():
            return

        # Create popup to get container parameters
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Container name input (optional)
        name_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        name_layout.add_widget(Label(text="Container name:", size_hint_x=0.3))
        name_input = TextInput(hint_text="Optional", size_hint_x=0.7)
        name_layout.add_widget(name_input)
        layout.add_widget(name_layout)

        # Port mapping input
        port_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        port_layout.add_widget(Label(text="Port mapping:", size_hint_x=0.3))
        port_input = TextInput(
            hint_text="host:container (e.g. 8080:80)", size_hint_x=0.7
        )
        port_layout.add_widget(port_input)
        layout.add_widget(port_layout)

        # Command input
        cmd_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        cmd_layout.add_widget(Label(text="Command:", size_hint_x=0.3))
        cmd_input = TextInput(hint_text="Optional", size_hint_x=0.7)
        cmd_layout.add_widget(cmd_input)
        layout.add_widget(cmd_layout)

        # Status output
        status_label = Label(
            text=f"Running image: {image_name}", size_hint_y=None, height=30
        )
        layout.add_widget(status_label)

        # Button layout
        btn_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=50)

        # Function to run container
        def do_run_container(btn):
            try:
                # Parse parameters
                name = name_input.text.strip() if name_input.text.strip() else None

                # Parse port mapping
                ports = {}
                if port_input.text.strip():
                    try:
                        host_port, container_port = port_input.text.strip().split(":")
                        ports = {container_port: host_port}
                    except ValueError:
                        status_label.text = "Invalid port format. Use host:container"
                        return

                # Get command
                command = cmd_input.text.strip() if cmd_input.text.strip() else None

                # Run container in a separate thread
                def run_thread():
                    try:
                        container = self.docker_client.containers.run(
                            image_name,
                            name=name,
                            ports=ports,
                            command=command,
                            detach=True,  # Run in background
                        )
                        Clock.schedule_once(
                            lambda dt: setattr(
                                status_label,
                                "text",
                                f"Container started: {container.short_id}",
                            ),
                            0,
                        )
                        # Update container list
                        Clock.schedule_once(lambda dt: self.update_image_list(), 1)

                    except Exception as e:
                        Clock.schedule_once(
                            lambda dt: setattr(
                                status_label, "text", f"Error: {str(e)}"
                            ),
                            0,
                        )

                status_label.text = f"Starting container from {image_name}..."
                threading.Thread(target=run_thread).start()

            except Exception as e:
                status_label.text = f"Error: {str(e)}"

        # Create run and cancel buttons
        run_btn = Button(text="Run Container")
        run_btn.bind(on_press=do_run_container)
        cancel_btn = Button(text="Close")
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        btn_layout.add_widget(run_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)

        # Create and open popup
        popup = Popup(title="Run Container", content=layout, size_hint=(0.8, 0.6))
        popup.open()

    def remove_image(self, image_name):
        """Remove a Docker image by name"""
        if not self._check_docker_client():
            return

        # Confirm dialog
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(
            Label(
                text=f"Are you sure you want to remove image {image_name}?\nThis action cannot be undone."
            )
        )

        btn_layout = BoxLayout(
            orientation="horizontal", spacing=10, size_hint_y=None, height=50
        )

        # Function to remove image
        def do_remove_image(btn):
            try:
                self.docker_client.images.remove(image_name, force=True)
                self.status_label.text = f"Successfully removed image {image_name}"
                self.update_image_list()
                popup.dismiss()
            except Exception as e:
                self.status_label.text = f"Error removing image: {str(e)}"
                popup.dismiss()

        # Create buttons
        cancel_btn = Button(text="Cancel")
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        remove_btn = Button(text="Remove", background_color=(1, 0.3, 0.3, 1))
        remove_btn.bind(on_press=do_remove_image)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(remove_btn)
        content.add_widget(btn_layout)

        # Create and open popup
        popup = Popup(title="Confirm Remove", content=content, size_hint=(0.7, 0.3))
        popup.open()

    def remove_image_by_id(self, image_id):
        """Remove a Docker image by ID"""
        if not self._check_docker_client():
            return

        # Confirm dialog
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(
            Label(
                text=f"Are you sure you want to remove image {image_id}?\nThis action cannot be undone."
            )
        )

        btn_layout = BoxLayout(
            orientation="horizontal", spacing=10, size_hint_y=None, height=50
        )

        # Function to remove image
        def do_remove_image(btn):
            try:
                self.docker_client.images.remove(image_id, force=True)
                self.status_label.text = f"Successfully removed image {image_id}"
                self.update_image_list()
                popup.dismiss()
            except Exception as e:
                self.status_label.text = f"Error removing image: {str(e)}"
                popup.dismiss()

        # Create buttons
        cancel_btn = Button(text="Cancel")
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        remove_btn = Button(text="Remove", background_color=(1, 0.3, 0.3, 1))
        remove_btn.bind(on_press=do_remove_image)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(remove_btn)
        content.add_widget(btn_layout)

        # Create and open popup
        popup = Popup(title="Confirm Remove", content=content, size_hint=(0.7, 0.3))
        popup.open()

    def pull_image(self, instance):
        """Pull a Docker image"""
        if not self._check_docker_client():
            return

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Image name input
        name_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        name_layout.add_widget(Label(text="Image name:tag:", size_hint_x=0.3))
        name_input = TextInput(text="ubuntu:latest", size_hint_x=0.7)
        name_layout.add_widget(name_input)
        layout.add_widget(name_layout)

        # Status label
        status_label = Label(
            text="Enter image name to pull", size_hint_y=None, height=30
        )
        layout.add_widget(status_label)

        # Button layout
        btn_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=50)

        # Function to pull image
        def do_pull_image(btn):
            image_name = name_input.text.strip()

            if not image_name:
                status_label.text = "Please enter an image name"
                return

            status_label.text = f"Pulling image {image_name}..."
            pull_btn.disabled = True

            # Pull image in a separate thread
            def pull_thread():
                try:
                    self.docker_client.images.pull(image_name)

                    Clock.schedule_once(
                        lambda dt: setattr(
                            status_label, "text", f"Successfully pulled {image_name}"
                        ),
                        0,
                    )
                    Clock.schedule_once(
                        lambda dt: setattr(pull_btn, "disabled", False), 0
                    )
                    Clock.schedule_once(lambda dt: self.update_image_list(), 1)

                except Exception as e:
                    Clock.schedule_once(
                        lambda dt: setattr(status_label, "text", f"Error: {str(e)}"), 0
                    )
                    Clock.schedule_once(
                        lambda dt: setattr(pull_btn, "disabled", False), 0
                    )

            threading.Thread(target=pull_thread).start()

        # Create pull and cancel buttons
        pull_btn = Button(text="Pull Image")
        pull_btn.bind(on_press=do_pull_image)

        cancel_btn = Button(text="Close")
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        btn_layout.add_widget(pull_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)

        # Create and open popup
        popup = Popup(title="Pull Docker Image", content=layout, size_hint=(0.8, 0.4))
        popup.open()

    def _check_docker_client(self):
        """Check if Docker client is available"""
        if not self.docker_available:
            try:
                self.docker_client = docker.from_env()
                self.docker_available = True
            except Exception as e:
                self.status_label.text = f"Docker not available: {str(e)}"
                return False
        return True

    def go_back(self, instance):
        """Return to Docker menu"""
        self.manager.current = "docker"


class DockerContainersScreen(Screen):
    def __init__(self, **kwargs):
        super(DockerContainersScreen, self).__init__(**kwargs)

        # Try to initialize the Docker client
        try:
            self.docker_client = docker.from_env()
            self.docker_available = True
        except Exception as e:
            self.docker_client = None
            self.docker_available = False

        # Main container with padding
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        self.add_widget(self.layout)

        # Title and header
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=50)
        title = Label(
            text="Docker Containers",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint=(0.7, 1),
        )
        header.add_widget(title)

        # Refresh button
        refresh_btn = Button(
            text="Refresh", size_hint=(0.3, 1), background_color=(0.3, 0.7, 1, 1)
        )
        refresh_btn.bind(on_press=lambda x: self.update_container_list())
        header.add_widget(refresh_btn)

        self.layout.add_widget(header)

        # Filter container
        filter_container = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=40, spacing=10
        )

        # Show all checkbox using a button for simplicity
        self.show_all_btn = Button(
            text="Show All Containers: No",
            size_hint=(0.5, 1),
            background_color=(0.3, 0.7, 1, 1),
        )
        self.show_all = False
        self.show_all_btn.bind(on_press=self.toggle_show_all)
        filter_container.add_widget(self.show_all_btn)

        # Status label
        self.status_label = Label(text="", size_hint=(0.5, 1))
        filter_container.add_widget(self.status_label)

        self.layout.add_widget(filter_container)

        # Containers list container
        containers_container = BoxLayout(orientation="vertical", spacing=10)

        # Column headers
        headers = GridLayout(cols=5, size_hint_y=None, height=40, spacing=2)
        headers.add_widget(Label(text="Container ID", bold=True))
        headers.add_widget(Label(text="Name", bold=True))
        headers.add_widget(Label(text="Image", bold=True))
        headers.add_widget(Label(text="Status", bold=True))
        headers.add_widget(Label(text="Actions", bold=True))
        containers_container.add_widget(headers)

        # Scroll view for container list
        scroll = ScrollView()
        self.container_list = GridLayout(cols=5, spacing=2, size_hint_y=None)
        self.container_list.bind(minimum_height=self.container_list.setter("height"))
        scroll.add_widget(self.container_list)
        containers_container.add_widget(scroll)

        self.layout.add_widget(containers_container)

        # Button container
        button_container = BoxLayout(
            orientation="horizontal", spacing=20, size_hint=(1, None), height=50
        )

        # Run Container button
        self.run_btn = Button(
            text="Run New Container",
            size_hint=(0.5, 1),
            background_color=(0.3, 0.7, 1, 1),
        )
        self.run_btn.bind(on_press=self.run_container)
        button_container.add_widget(self.run_btn)

        # Back button
        self.back_btn = Button(
            text="Back", size_hint=(0.5, 1), background_color=(0.3, 0.7, 1, 1)
        )
        self.back_btn.bind(on_press=self.go_back)
        button_container.add_widget(self.back_btn)

        self.layout.add_widget(button_container)

    def on_enter(self):
        self.update_container_list()

    def toggle_show_all(self, instance):
        """Toggle showing all containers vs only running ones"""
        self.show_all = not self.show_all
        self.show_all_btn.text = (
            f"Show All Containers: {'Yes' if self.show_all else 'No'}"
        )
        self.update_container_list()

    def update_container_list(self):
        """Refresh the list of Docker containers"""
        self.container_list.clear_widgets()

        if not self._check_docker_client():
            self.status_label.text = "Docker is not available"
            return

        try:
            # Change status
            self.status_label.text = "Loading Docker containers..."

            # Get all Docker containers
            containers = self.docker_client.containers.list(all=self.show_all)

            if not containers:
                state = "all" if self.show_all else "running"
                self.status_label.text = f"No {state} containers found"
                return

            # Add each container to the list
            for container in containers:
                # Add container ID (shortened)
                container_id = container.short_id
                self.container_list.add_widget(
                    Label(text=container_id, size_hint_y=None, height=40)
                )

                # Add container name
                self.container_list.add_widget(
                    Label(text=container.name, size_hint_y=None, height=40)
                )

                # Add image name (shortened if necessary)
                image_name = (
                    container.image.tags[0]
                    if container.image.tags
                    else container.image.short_id
                )
                if len(image_name) > 20:
                    image_name = image_name[:17] + "..."

                self.container_list.add_widget(
                    Label(text=image_name, size_hint_y=None, height=40)
                )

                # Add status
                status = container.status
                status_color = (0, 1, 0, 1) if status == "running" else (1, 0.5, 0, 1)
                status_label = Label(
                    text=status, size_hint_y=None, height=40, color=status_color
                )
                self.container_list.add_widget(status_label)

                # Add action buttons
                action_layout = BoxLayout(
                    orientation="horizontal", spacing=5, size_hint_y=None, height=40
                )

                # Different buttons depending on container state
                if container.status == "running":
                    # Stop button
                    stop_btn = Button(
                        text="Stop", size_hint_x=0.5, background_color=(1, 0.5, 0, 1)
                    )
                    stop_btn.bind(
                        on_press=lambda x, c=container.id: self.stop_container(c)
                    )
                    action_layout.add_widget(stop_btn)

                    # Logs button
                    logs_btn = Button(
                        text="Logs", size_hint_x=0.5, background_color=(0.3, 0.7, 1, 1)
                    )
                    logs_btn.bind(on_press=lambda x, c=container.id: self.view_logs(c))
                    action_layout.add_widget(logs_btn)
                else:
                    # Start button
                    start_btn = Button(
                        text="Start", size_hint_x=0.5, background_color=(0, 0.7, 0, 1)
                    )
                    start_btn.bind(
                        on_press=lambda x, c=container.id: self.start_container(c)
                    )
                    action_layout.add_widget(start_btn)

                    # Remove button
                    remove_btn = Button(
                        text="Remove",
                        size_hint_x=0.5,
                        background_color=(1, 0.3, 0.3, 1),
                    )
                    remove_btn.bind(
                        on_press=lambda x, c=container.id: self.remove_container(c)
                    )
                    action_layout.add_widget(remove_btn)

                self.container_list.add_widget(action_layout)

            state = "all" if self.show_all else "running"
            self.status_label.text = f"Found {len(containers)} {state} containers"

        except Exception as e:
            self.status_label.text = f"Error loading containers: {str(e)}"

    def stop_container(self, container_id):
        """Stop a running container"""
        if not self._check_docker_client():
            return

        try:
            container = self.docker_client.containers.get(container_id)
            container.stop()
            self.status_label.text = f"Stopped container {container.name}"
            self.update_container_list()
        except Exception as e:
            self.status_label.text = f"Error stopping container: {str(e)}"

    def start_container(self, container_id):
        """Start a stopped container"""
        if not self._check_docker_client():
            return

        try:
            container = self.docker_client.containers.get(container_id)
            container.start()
            self.status_label.text = f"Started container {container.name}"
            self.update_container_list()
        except Exception as e:
            self.status_label.text = f"Error starting container: {str(e)}"

    def remove_container(self, container_id):
        """Remove a stopped container"""
        if not self._check_docker_client():
            return

        # Confirm dialog
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)

        try:
            container = self.docker_client.containers.get(container_id)
            content.add_widget(
                Label(
                    text=f"Are you sure you want to remove container {container.name}?\nThis action cannot be undone."
                )
            )
        except:
            content.add_widget(
                Label(
                    text=f"Are you sure you want to remove this container?\nThis action cannot be undone."
                )
            )

        btn_layout = BoxLayout(
            orientation="horizontal", spacing=10, size_hint_y=None, height=50
        )

        # Function to remove container
        def do_remove_container(btn):
            try:
                container = self.docker_client.containers.get(container_id)
                name = container.name
                container.remove(force=True)  # Force removal even if running
                self.status_label.text = f"Successfully removed container {name}"
                self.update_container_list()
                popup.dismiss()
            except Exception as e:
                self.status_label.text = f"Error removing container: {str(e)}"
                popup.dismiss()

        # Create buttons
        cancel_btn = Button(text="Cancel")
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        remove_btn = Button(text="Remove", background_color=(1, 0.3, 0.3, 1))
        remove_btn.bind(on_press=do_remove_container)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(remove_btn)
        content.add_widget(btn_layout)

        # Create and open popup
        popup = Popup(title="Confirm Remove", content=content, size_hint=(0.7, 0.3))
        popup.open()

    def view_logs(self, container_id):
        """View container logs"""
        if not self._check_docker_client():
            return

        try:
            container = self.docker_client.containers.get(container_id)

            # Create popup to display logs
            layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            # Container info
            info_text = f"Container: {container.name}\n"
            info_text += f"Image: {container.image.tags[0] if container.image.tags else container.image.short_id}\n"
            info_text += f"Status: {container.status}\n\n"

            layout.add_widget(
                Label(
                    text=info_text,
                    size_hint_y=None,
                    height=80,
                    halign="left",
                    valign="top",
                )
            )

            # Function to get logs
            def get_logs():
                try:
                    # Get logs with tail limit to avoid huge logs
                    logs = container.logs(tail=100).decode("utf-8")
                    return logs if logs else "No logs available"
                except Exception as e:
                    return f"Error retrieving logs: {str(e)}"

            # Get logs in a separate thread
            def get_logs_thread():
                logs = get_logs()
                Clock.schedule_once(lambda dt: setattr(log_output, "text", logs), 0)

            # Logs output
            log_output = TextInput(
                readonly=True, multiline=True, text="Loading logs..."
            )
            layout.add_widget(log_output)

            # Start the logs thread
            threading.Thread(target=get_logs_thread).start()

            # Refresh button
            refresh_btn = Button(text="Refresh Logs", size_hint_y=None, height=40)
            refresh_btn.bind(
                on_press=lambda x: threading.Thread(target=get_logs_thread).start()
            )
            layout.add_widget(refresh_btn)

            # Close button
            close_btn = Button(text="Close", size_hint_y=None, height=40)
            close_btn.bind(on_press=lambda x: popup.dismiss())
            layout.add_widget(close_btn)

            # Create and open popup
            popup = Popup(
                title=f"Logs - {container.name}", content=layout, size_hint=(0.9, 0.9)
            )
            popup.open()

        except Exception as e:
            self.status_label.text = f"Error viewing logs: {str(e)}"

    def run_container(self, instance):
        """Run a new container from an image"""
        if not self._check_docker_client():
            return

        # Get list of available images
        try:
            images = self.docker_client.images.list()
            image_tags = []
            for image in images:
                if image.tags:
                    image_tags.extend(image.tags)
        except:
            image_tags = []

        # Create popup for container parameters
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Image selection
        image_layout = BoxLayout(
            orientation="vertical", size_hint_y=None, height=80, spacing=5
        )
        image_layout.add_widget(
            Label(text="Select or enter image:", size_hint_y=None, height=20)
        )

        image_spinner = Spinner(
            text="Select image" if image_tags else "No images available",
            values=image_tags,
            size_hint_y=None,
            height=40,
        )

        image_input = TextInput(
            hint_text="Or type image name (e.g. ubuntu:latest)",
            multiline=False,
            size_hint_y=None,
            height=40,
        )

        # Function to update text input when spinner is selected
        def on_spinner_select(spinner, text):
            image_input.text = text

        image_spinner.bind(text=on_spinner_select)

        image_layout.add_widget(image_spinner)
        image_layout.add_widget(image_input)
        layout.add_widget(image_layout)

        # Container name (optional)
        name_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
        name_layout.add_widget(Label(text="Container name:", size_hint_x=0.3))
        name_input = TextInput(hint_text="Optional", size_hint_x=0.7)
        name_layout.add_widget(name_input)
        layout.add_widget(name_layout)

        # Port mapping
        port_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
        port_layout.add_widget(Label(text="Port mapping:", size_hint_x=0.3))
        port_input = TextInput(
            hint_text="host:container (e.g. 8080:80)", size_hint_x=0.7
        )
        port_layout.add_widget(port_input)
        layout.add_widget(port_layout)

        # Command
        cmd_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
        cmd_layout.add_widget(Label(text="Command:", size_hint_x=0.3))
        cmd_input = TextInput(hint_text="Optional", size_hint_x=0.7)
        cmd_layout.add_widget(cmd_input)
        layout.add_widget(cmd_layout)

        # Status message
        status_label = Label(
            text="Configure container parameters", size_hint_y=None, height=40
        )
        layout.add_widget(status_label)

        # Button layout
        btn_layout = BoxLayout(
            orientation="horizontal", spacing=10, size_hint_y=None, height=50
        )

        # Function to run container
        def do_run_container(btn):
            try:
                # Get parameters
                image_name = image_input.text.strip()
                if not image_name:
                    status_label.text = "Please enter an image name"
                    return

                # Optional name
                name = name_input.text.strip() if name_input.text.strip() else None

                # Parse port mapping
                ports = {}
                if port_input.text.strip():
                    try:
                        host_port, container_port = port_input.text.strip().split(":")
                        ports = {container_port: host_port}
                    except ValueError:
                        status_label.text = "Invalid port format. Use host:container"
                        return

                # Optional command
                command = cmd_input.text.strip() if cmd_input.text.strip() else None

                # Run container in a thread
                def run_thread():
                    try:
                        container = self.docker_client.containers.run(
                            image_name,
                            name=name,
                            ports=ports,
                            command=command,
                            detach=True,
                        )

                        # Update UI
                        Clock.schedule_once(
                            lambda dt: setattr(
                                status_label,
                                "text",
                                f"Container {container.name} started successfully",
                            ),
                            0,
                        )

                        # Close popup after success
                        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

                        # Update container list
                        Clock.schedule_once(lambda dt: self.update_container_list(), 2)

                    except Exception as e:
                        Clock.schedule_once(
                            lambda dt: setattr(
                                status_label, "text", f"Error: {str(e)}"
                            ),
                            0,
                        )

                status_label.text = "Starting container..."
                threading.Thread(target=run_thread).start()

            except Exception as e:
                status_label.text = f"Error: {str(e)}"

        # Create run and cancel buttons
        run_btn = Button(text="Run Container")
        run_btn.bind(on_press=do_run_container)

        cancel_btn = Button(text="Cancel")
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        btn_layout.add_widget(run_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)

        # Create and open popup
        popup = Popup(title="Run Container", content=layout, size_hint=(0.8, 0.8))
        popup.open()

    def _check_docker_client(self):
        """Check if Docker client is available"""
        if not self.docker_available:
            try:
                self.docker_client = docker.from_env()
                self.docker_available = True
            except Exception as e:
                self.status_label.text = f"Docker not available: {str(e)}"
                return False
        return True

    def go_back(self, instance):
        """Return to Docker menu"""
        self.manager.current = "docker"


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
            height=50,
        )
        self.layout.add_widget(title)

        # Input fields container
        input_container = BoxLayout(
            orientation="vertical", spacing=20, size_hint=(1, 0.6)
        )

        # Disk name input
        self.disk_name = TextInput(
            hint_text="Enter disk name",
            multiline=False,
            size_hint=(1, None),
            height=50,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
        )
        input_container.add_widget(self.disk_name)

        # Disk size input
        self.disk_size = TextInput(
            hint_text="Enter disk size in GB",
            multiline=False,
            size_hint=(1, None),
            height=50,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
        )
        input_container.add_widget(self.disk_size)

        # Disk format dropdown
        self.disk_format = Spinner(
            text="Select disk format",
            values=["qcow2", "raw", "vmdk", "vhdx"],
            size_hint=(1, None),
            height=50,
            background_color=(0.1, 0.1, 0.1, 1),
        )
        input_container.add_widget(self.disk_format)

        self.layout.add_widget(input_container)

        # Button container
        button_container = BoxLayout(
            orientation="horizontal", spacing=20, size_hint=(1, None), height=50
        )

        # Back button
        self.back_btn = Button(
            text="Back", size_hint=(0.3, 1), background_color=(0.3, 0.7, 1, 1)
        )
        self.back_btn.bind(on_press=self.go_back)
        button_container.add_widget(self.back_btn)

        # Create Disk button
        self.create_disk_btn = Button(
            text="Create Disk", size_hint=(0.7, 1), background_color=(0.3, 0.7, 1, 1)
        )
        self.create_disk_btn.bind(on_press=self.create_disk)
        button_container.add_widget(self.create_disk_btn)

        self.layout.add_widget(button_container)

    def go_back(self, instance):
        self.manager.current = "vm_selection"

    def create_disk(self, instance):
        disk_name = self.disk_name.text.strip()
        disk_size = self.disk_size.text.strip()
        disk_format = self.disk_format.text

        if not disk_name or not disk_size:
            self.show_error("Please fill in all fields")
            return

        try:
            disk_size = int(disk_size)
            if disk_size <= 0:
                raise ValueError
        except ValueError:
            self.show_error("Please enter a valid disk size (positive integer)")
            return

        # Get the disk directory
        disk_dir = get_disk_directory()
        if not disk_dir:
            self.show_error("Failed to access or create disk directory")
            return

        print(f"Creating disk in directory: {disk_dir}")  # Debug print

        disk_path = os.path.join(disk_dir, f"{disk_name}.{disk_format}")
        print(f"Full disk path: {disk_path}")  # Debug print

        try:
            # Create the disk using qemu-img
            subprocess.run(
                ["qemu-img", "create", "-f", disk_format, disk_path, f"{disk_size}G"],
                check=True,
            )

            print(f"Disk created successfully at: {disk_path}")  # Debug print
            print(f"Disk file exists: {os.path.exists(disk_path)}")  # Debug print

            self.show_success(f"Disk created successfully")

            # Update the disk list in the VM screen before switching
            vm_screen = self.manager.get_screen("vm")
            vm_screen.disk_selection.values = vm_screen.get_available_disks()

            self.manager.current = "vm_selection"
        except subprocess.CalledProcessError as e:
            print(f"Error creating disk: {str(e)}")  # Debug print
            self.show_error(f"Failed to create disk: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # Debug print
            self.show_error(f"An error occurred: {str(e)}")

    def show_error(self, message):
        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

    def show_success(self, message):
        popup = Popup(
            title="Success",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()


# VM Properties screen
class VMScreen(Screen):
    def __init__(self, **kwargs):
        super(VMScreen, self).__init__(**kwargs)

        # Main container with padding
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        self.add_widget(self.layout)

        # Title
        title = Label(
            text="Create Virtual Machine",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint=(1, None),
            height=50,
        )
        self.layout.add_widget(title)

        # Input fields container
        input_container = BoxLayout(
            orientation="vertical", spacing=20, size_hint=(1, 0.6)
        )

        # VM name input
        self.vm_name = TextInput(
            hint_text="Enter VM name",
            multiline=False,
            size_hint=(1, None),
            height=50,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
        )
        input_container.add_widget(self.vm_name)

        # Memory input
        self.memory = TextInput(
            hint_text="Enter memory size in GB",
            multiline=False,
            size_hint=(1, None),
            height=50,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
        )
        input_container.add_widget(self.memory)

        # CPU cores input
        self.cpu_cores = TextInput(
            hint_text="Enter number of CPU cores",
            multiline=False,
            size_hint=(1, None),
            height=50,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
        )
        input_container.add_widget(self.cpu_cores)

        # ISO file selection
        iso_container = BoxLayout(
            orientation="horizontal", spacing=10, size_hint=(1, None), height=50
        )

        self.iso_path = TextInput(
            hint_text="ISO file path",
            multiline=False,
            size_hint=(0.7, 1),
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            readonly=True,
        )
        iso_container.add_widget(self.iso_path)

        self.select_iso_btn = Button(
            text="Select ISO", size_hint=(0.3, 1), background_color=(0.3, 0.7, 1, 1)
        )
        self.select_iso_btn.bind(on_press=self.select_iso)
        iso_container.add_widget(self.select_iso_btn)

        input_container.add_widget(iso_container)

        # Disk selection
        self.disk_selection = Spinner(
            text="Select virtual disk",
            values=self.get_available_disks(),
            size_hint=(1, None),
            height=50,
            background_color=(0.1, 0.1, 0.1, 1),
        )
        input_container.add_widget(self.disk_selection)

        self.layout.add_widget(input_container)

        # Button container
        button_container = BoxLayout(
            orientation="horizontal", spacing=20, size_hint=(1, None), height=50
        )

        # Back button
        self.back_btn = Button(
            text="Back", size_hint=(0.3, 1), background_color=(0.3, 0.7, 1, 1)
        )
        self.back_btn.bind(on_press=self.go_back)
        button_container.add_widget(self.back_btn)

        # Create VM button
        self.create_vm_btn = Button(
            text="Create VM", size_hint=(0.7, 1), background_color=(0.3, 0.7, 1, 1)
        )
        self.create_vm_btn.bind(on_press=self.create_vm)
        button_container.add_widget(self.create_vm_btn)

        self.layout.add_widget(button_container)

    def select_iso(self, instance):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select ISO file",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")],
        )
        if file_path:
            self.iso_path.text = file_path

    def get_available_disks(self):
        disk_dir = get_disk_directory()
        if not disk_dir:
            return ["No disks available"]

        disks = []
        for file in os.listdir(disk_dir):
            if file.endswith((".qcow2", ".raw", ".vmdk", ".vhdx")):
                disks.append(file)

        return disks if disks else ["No disks available"]

    def go_back(self, instance):
        self.manager.current = "vm_selection"

    def create_vm(self, instance):
        vm_name = self.vm_name.text.strip()
        memory = self.memory.text.strip()  # Now in GB
        cpu_cores = self.cpu_cores.text.strip()
        selected_disk = self.disk_selection.text
        iso_path = self.iso_path.text.strip()

        if (
            not all([vm_name, memory, cpu_cores])
            or selected_disk == "No disks available"
        ):
            self.show_error(
                "Please fill in all required fields (VM name, memory, CPU cores) and select a disk"
            )
            return

        try:
            memory_gb = float(memory)  # Convert to float to handle decimal GB values
            if memory_gb <= 0:
                raise ValueError
            memory_mb = int(memory_gb * 1024)  # Convert GB to MB
            cpu_cores = int(cpu_cores)
            if cpu_cores <= 0:
                raise ValueError
        except ValueError:
            self.show_error("Please enter valid memory (GB) and CPU core values")
            return

        # Check for MSYS2 installation
        msys_path = find_msys64()
        if not msys_path:
            self.show_error(
                "MSYS2 not found. Please install MSYS2 from https://www.msys2.org/"
            )
            return

        # Check if mingw64.exe exists
        qemu_path = os.path.join(msys_path, "mingw64.exe")
        if not os.path.exists(qemu_path):
            self.show_error(f"mingw64.exe not found at {qemu_path}")
            return

        disk_dir = get_disk_directory()
        disk_path = os.path.join(disk_dir, selected_disk)

        if not os.path.exists(disk_path):
            self.show_error(f"Selected disk file not found: {disk_path}")
            return

        if iso_path and not os.path.exists(iso_path):
            self.show_error(f"Selected ISO file not found: {iso_path}")
            return

        try:
            # Create a batch file to run the VM
            batch_file = os.path.join(disk_dir, f"{vm_name}.bat")
            with open(batch_file, "w") as f:
                if iso_path:
                    f.write(
                        f'start "" "{qemu_path}" qemu-system-x86_64 -hda "{disk_path}" -cdrom "{iso_path}" -boot d -m {memory_mb} -smp {cpu_cores}\n'
                    )
                else:
                    f.write(
                        f'start "" "{qemu_path}" qemu-system-x86_64 -hda "{disk_path}" -boot d -m {memory_mb} -smp {cpu_cores}\n'
                    )

            # Show success popup with launch option
            content = BoxLayout(orientation="vertical", spacing=10, padding=10)
            content.add_widget(Label(text=f"VM {vm_name} created successfully!"))

            btn_layout = BoxLayout(
                orientation="horizontal", spacing=10, size_hint_y=None, height=50
            )
            launch_btn = Button(text="Launch Now", background_color=(0.3, 0.7, 1, 1))
            close_btn = Button(text="Close")

            def launch_vm(instance):
                try:
                    subprocess.run([batch_file], shell=True, check=True)
                    popup.dismiss()
                    self.manager.current = "vm_selection"
                except Exception as e:
                    self.show_error(f"Failed to launch VM: {str(e)}")

            launch_btn.bind(on_press=launch_vm)
            close_btn.bind(on_press=lambda x: popup.dismiss())

            btn_layout.add_widget(launch_btn)
            btn_layout.add_widget(close_btn)
            content.add_widget(btn_layout)

            popup = Popup(
                title="VM Created Successfully",
                content=content,
                size_hint=(None, None),
                size=(400, 200),
            )
            popup.open()

            self.manager.current = "vm_selection"
        except subprocess.CalledProcessError as e:
            self.show_error(f"Failed to create VM: {str(e)}")
        except FileNotFoundError:
            self.show_error("Failed to create or run the VM batch file.")
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")

    def show_error(self, message):
        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

    def show_success(self, message):
        popup = Popup(
            title="Success",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()


class ExistingVMsScreen(Screen):
    def __init__(self, **kwargs):
        super(ExistingVMsScreen, self).__init__(**kwargs)

        # Main container with padding
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        self.add_widget(self.layout)

        # Title and header
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=50)
        title = Label(
            text="Existing Virtual Machines",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint=(0.8, 1),
        )
        header.add_widget(title)

        # Refresh button
        refresh_btn = Button(
            text="Refresh", size_hint=(0.2, 1), background_color=(0.3, 0.7, 1, 1)
        )
        refresh_btn.bind(on_press=lambda x: self.update_vm_list())
        header.add_widget(refresh_btn)

        self.layout.add_widget(header)

        # VM list container
        vm_container = BoxLayout(orientation="vertical", spacing=10)

        # Column headers
        headers = GridLayout(cols=2, size_hint_y=None, height=40)
        headers.add_widget(Label(text="VM Name", bold=True))
        headers.add_widget(Label(text="Actions", bold=True))
        vm_container.add_widget(headers)

        # Scroll view for VM list
        scroll = ScrollView()
        self.vm_list = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.vm_list.bind(minimum_height=self.vm_list.setter("height"))
        scroll.add_widget(self.vm_list)
        vm_container.add_widget(scroll)

        self.layout.add_widget(vm_container)

        # Back button
        self.back_btn = Button(
            text="Back",
            size_hint=(0.3, None),
            height=50,
            background_color=(0.3, 0.7, 1, 1),
            pos_hint={"center_x": 0.5},
        )
        self.back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_btn)

    def on_enter(self):
        self.update_vm_list()

    def update_vm_list(self):
        self.vm_list.clear_widgets()
        msys_path = find_msys64()
        if not msys_path:
            self.vm_list.add_widget(
                Label(
                    text="MSYS2 not found. Please install MSYS2.",
                    color=(1, 0, 0, 1),
                    size_hint_y=None,
                    height=50,
                )
            )
            return

        disk_dir = get_disk_directory()
        if not disk_dir:
            self.vm_list.add_widget(
                Label(
                    text="Failed to access disk directory",
                    color=(1, 0, 0, 1),
                    size_hint_y=None,
                    height=50,
                )
            )
            return

        if not os.path.exists(disk_dir):
            self.vm_list.add_widget(
                Label(
                    text="No VMs found", color=(1, 1, 1, 1), size_hint_y=None, height=50
                )
            )
            return

        # Find all .bat files (VM configurations)
        vm_files = [f for f in os.listdir(disk_dir) if f.endswith(".bat")]
        if not vm_files:
            self.vm_list.add_widget(
                Label(
                    text="No VMs found", color=(1, 1, 1, 1), size_hint_y=None, height=50
                )
            )
            return

        for vm_file in vm_files:
            vm_name = os.path.splitext(vm_file)[0]

            # VM name
            self.vm_list.add_widget(Label(text=vm_name, size_hint_y=None, height=50))

            # Action buttons container
            btn_container = BoxLayout(
                orientation="horizontal", spacing=5, size_hint_y=None, height=50
            )

            # Start button
            start_btn = Button(
                text="Start", size_hint=(0.5, 1), background_color=(0.3, 0.7, 1, 1)
            )
            start_btn.bind(on_press=lambda x, name=vm_name: self.start_vm(name))
            btn_container.add_widget(start_btn)

            # Delete button
            delete_btn = Button(
                text="Delete", size_hint=(0.5, 1), background_color=(1, 0.3, 0.3, 1)
            )
            delete_btn.bind(on_press=lambda x, name=vm_name: self.delete_vm(name))
            btn_container.add_widget(delete_btn)

            self.vm_list.add_widget(btn_container)

    def start_vm(self, vm_name):
        msys_path = find_msys64()
        if not msys_path:
            self.show_error("MSYS2 not found")
            return

        disk_dir = get_disk_directory()
        if not disk_dir:
            self.show_error("Failed to access disk directory")
            return

        batch_file = os.path.join(disk_dir, f"{vm_name}.bat")

        if not os.path.exists(batch_file):
            self.show_error(f"VM configuration not found: {vm_name}")
            return

        try:
            subprocess.run([batch_file], shell=True, check=True)
            self.show_success(f"Starting VM: {vm_name}")
        except Exception as e:
            self.show_error(f"Failed to start VM: {str(e)}")

    def delete_vm(self, vm_name):
        def confirm_delete(instance):
            try:
                msys_path = find_msys64()
                if not msys_path:
                    raise Exception("MSYS2 not found")

                disk_dir = get_disk_directory()
                if not disk_dir:
                    raise Exception("Failed to access disk directory")

                batch_file = os.path.join(disk_dir, f"{vm_name}.bat")

                if os.path.exists(batch_file):
                    os.remove(batch_file)
                    self.show_success(f"VM {vm_name} deleted successfully")
                    self.update_vm_list()
                else:
                    raise Exception(f"VM configuration not found: {vm_name}")
            except Exception as e:
                self.show_error(f"Failed to delete VM: {str(e)}")
            popup.dismiss()

        popup = Popup(
            title="Confirm Delete",
            content=BoxLayout(orientation="vertical", spacing=10, padding=10),
            size_hint=(None, None),
            size=(400, 200),
        )

        content = popup.content
        content.add_widget(
            Label(
                text=f"Are you sure you want to delete {vm_name}?\nThis action cannot be undone."
            )
        )

        btn_layout = BoxLayout(
            orientation="horizontal", spacing=10, size_hint_y=None, height=50
        )
        cancel_btn = Button(text="Cancel")
        delete_btn = Button(text="Delete", background_color=(1, 0.3, 0.3, 1))

        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        delete_btn.bind(on_press=confirm_delete)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(delete_btn)
        content.add_widget(btn_layout)

        popup.open()

    def show_error(self, message):
        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

    def show_success(self, message):
        popup = Popup(
            title="Success",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

    def go_back(self, instance):
        self.manager.current = "vm_selection"


class DiskManagementScreen(Screen):
    def __init__(self, **kwargs):
        super(DiskManagementScreen, self).__init__(**kwargs)

        # Main container with padding
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        self.add_widget(self.layout)

        # Title and header
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=50)
        title = Label(
            text="Virtual Disk Management",
            font_size=32,
            bold=True,
            color=(0.3, 0.7, 1, 1),
            size_hint=(0.8, 1),
        )
        header.add_widget(title)

        # Refresh button
        refresh_btn = Button(
            text="Refresh", size_hint=(0.2, 1), background_color=(0.3, 0.7, 1, 1)
        )
        refresh_btn.bind(on_press=lambda x: self.update_disk_list())
        header.add_widget(refresh_btn)

        self.layout.add_widget(header)

        # Disk list container
        disk_container = BoxLayout(orientation="vertical", spacing=10)

        # Column headers
        headers = GridLayout(cols=3, size_hint_y=None, height=40)
        headers.add_widget(Label(text="Disk Name", bold=True))
        headers.add_widget(Label(text="Format", bold=True))
        headers.add_widget(Label(text="Actions", bold=True))
        disk_container.add_widget(headers)

        # Scroll view for disk list
        scroll = ScrollView()
        self.disk_list = GridLayout(cols=3, spacing=10, size_hint_y=None)
        self.disk_list.bind(minimum_height=self.disk_list.setter("height"))
        scroll.add_widget(self.disk_list)
        disk_container.add_widget(scroll)

        self.layout.add_widget(disk_container)

        # Back button
        self.back_btn = Button(
            text="Back",
            size_hint=(0.3, None),
            height=50,
            background_color=(0.3, 0.7, 1, 1),
            pos_hint={"center_x": 0.5},
        )
        self.back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_btn)

    def on_enter(self):
        self.update_disk_list()

    def update_disk_list(self):
        self.disk_list.clear_widgets()

        # Get the disk directory
        disk_dir = get_disk_directory()
        if not disk_dir:
            self.disk_list.add_widget(
                Label(
                    text="Failed to access disk directory",
                    color=(1, 0, 0, 1),
                    size_hint_y=None,
                    height=50,
                )
            )
            return

        print(f"Looking for disks in: {disk_dir}")  # Debug print

        if not os.path.exists(disk_dir):
            print(f"Disk directory does not exist: {disk_dir}")  # Debug print
            self.disk_list.add_widget(
                Label(
                    text="No disks found",
                    color=(1, 1, 1, 1),
                    size_hint_y=None,
                    height=50,
                )
            )
            return

        # Find all disk files
        disk_files = [
            f
            for f in os.listdir(disk_dir)
            if f.endswith((".qcow2", ".raw", ".vmdk", ".vhdx"))
        ]
        print(f"Found disk files: {disk_files}")  # Debug print

        if not disk_files:
            self.disk_list.add_widget(
                Label(
                    text="No disks found",
                    color=(1, 1, 1, 1),
                    size_hint_y=None,
                    height=50,
                )
            )
            return

        for disk_file in disk_files:
            disk_name = os.path.splitext(disk_file)[0]
            disk_path = os.path.join(disk_dir, disk_file)
            disk_format = os.path.splitext(disk_file)[1][1:]  # Remove the dot

            # Add disk info to the list
            self.disk_list.add_widget(
                Label(text=disk_name, size_hint_y=None, height=50)
            )
            self.disk_list.add_widget(
                Label(text=disk_format.upper(), size_hint_y=None, height=50)
            )

            # Delete button
            delete_btn = Button(
                text="Delete",
                size_hint_y=None,
                height=50,
                background_color=(1, 0.3, 0.3, 1),
            )
            delete_btn.bind(
                on_press=lambda x, path=disk_path, name=disk_name: self.delete_disk(
                    path, name
                )
            )
            self.disk_list.add_widget(delete_btn)

    def delete_disk(self, disk_path, disk_name):
        def confirm_delete(instance):
            try:
                os.remove(disk_path)
                self.show_success(f"Disk {disk_name} deleted successfully")
                self.update_disk_list()

                # Update the disk list in the VM screen
                vm_screen = self.manager.get_screen("vm")
                vm_screen.disk_selection.values = vm_screen.get_available_disks()
                if disk_name in vm_screen.disk_selection.values:
                    vm_screen.disk_selection.text = "Select virtual disk"

            except Exception as e:
                self.show_error(f"Failed to delete disk: {str(e)}")
            popup.dismiss()

        popup = Popup(
            title="Confirm Delete",
            content=BoxLayout(orientation="vertical", spacing=10, padding=10),
            size_hint=(None, None),
            size=(400, 200),
        )

        content = popup.content
        content.add_widget(
            Label(
                text=f"Are you sure you want to delete {disk_name}?\nThis action cannot be undone."
            )
        )

        btn_layout = BoxLayout(
            orientation="horizontal", spacing=10, size_hint_y=None, height=50
        )
        cancel_btn = Button(text="Cancel")
        delete_btn = Button(text="Delete", background_color=(1, 0.3, 0.3, 1))

        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        delete_btn.bind(on_press=confirm_delete)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(delete_btn)
        content.add_widget(btn_layout)

        popup.open()

    def show_error(self, message):
        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

    def show_success(self, message):
        popup = Popup(
            title="Success",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

    def go_back(self, instance):
        self.manager.current = "vm_selection"


# Main App
class CloudApp(App):
    def build(self):
        Config.set("kivy", "keyboard_mode", "system")
        Config.set("kivy", "keyboard_layout", "qwerty")
        Config.set("kivy", "keyboard_type", "text")

        # Check for MSYS64 before proceeding
        msys_path = find_msys64()
        if msys_path is None:
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label

            popup = Popup(
                title="Error",
                content=Label(
                    text="MSYS64 not found in PATH. Please install MSYS64 and add it to your PATH environment variable."
                ),
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
