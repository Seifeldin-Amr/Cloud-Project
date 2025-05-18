from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown

import os
import subprocess


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