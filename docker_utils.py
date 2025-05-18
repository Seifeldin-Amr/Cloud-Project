from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown

import os
import threading
import time

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    docker = None
    DOCKER_AVAILABLE = False

# Placeholder classes to split from main
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
