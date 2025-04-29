import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading

class CloudManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Cloud Management System")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Set application icon and theme
        self.root.option_add("*Font", "Arial 10")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Cloud Management System", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create VM tab
        self.create_vm_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.create_vm_tab, text="Create VM")
        
        # VM creation form
        self.create_vm_form()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_vm_form(self):
        """Create the VM creation form"""
        form_frame = ttk.LabelFrame(self.create_vm_tab, text="Virtual Machine Configuration", padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # System resources section
        resources_frame = ttk.LabelFrame(form_frame, text="System Resources", padding="10")
        resources_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # RAM size
        ram_frame = ttk.Frame(resources_frame)
        ram_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ram_frame, text="RAM Size:").pack(side=tk.LEFT, padx=(0, 10))
        self.ram_size_var = tk.StringVar(value="2")
        ram_entry = ttk.Entry(ram_frame, textvariable=self.ram_size_var, width=10)
        ram_entry.pack(side=tk.LEFT)
        ttk.Label(ram_frame, text="GB").pack(side=tk.LEFT, padx=(5, 0))
        
        # CPU Cores
        cores_frame = ttk.Frame(resources_frame)
        cores_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cores_frame, text="CPU Cores:").pack(side=tk.LEFT, padx=(0, 10))
        self.cpu_cores_var = tk.StringVar(value="2")
        cores_entry = ttk.Entry(cores_frame, textvariable=self.cpu_cores_var, width=10)
        cores_entry.pack(side=tk.LEFT)
        
        # Disk configuration section
        disk_frame = ttk.LabelFrame(form_frame, text="Virtual Disk Configuration", padding="10")
        disk_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Disk size
        size_frame = ttk.Frame(disk_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="Disk Size (GB):").pack(side=tk.LEFT, padx=(0, 10))
        self.disk_size_var = tk.StringVar(value="10")
        size_entry = ttk.Entry(size_frame, textvariable=self.disk_size_var, width=10)
        size_entry.pack(side=tk.LEFT)
        ttk.Label(size_frame, text="GB").pack(side=tk.LEFT, padx=(5, 0))
        
        # Disk format
        format_frame = ttk.Frame(disk_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="Disk Format:").pack(side=tk.LEFT, padx=(0, 10))
        self.disk_format_var = tk.StringVar(value="qcow2")
        formats = ["qcow2", "raw", "vmdk", "vhdx"]
        format_dropdown = ttk.Combobox(format_frame, textvariable=self.disk_format_var, 
                                     values=formats, state="readonly", width=10)
        format_dropdown.pack(side=tk.LEFT)
        
        # Storage path
        path_frame = ttk.Frame(disk_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="Storage Path:").pack(side=tk.LEFT, padx=(0, 10))
        self.storage_path_var = tk.StringVar(value=os.path.expanduser("~/vm_disks"))
        path_entry = ttk.Entry(path_frame, textvariable=self.storage_path_var, width=40)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_storage_path)
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Disk name
        name_frame = ttk.Frame(disk_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="Disk Name:").pack(side=tk.LEFT, padx=(0, 10))
        self.disk_name_var = tk.StringVar(value="vm_disk")
        name_entry = ttk.Entry(name_frame, textvariable=self.disk_name_var, width=30)
        name_entry.pack(side=tk.LEFT)
        
        # Create VM button
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(pady=20)
        
        create_button = ttk.Button(button_frame, text="Create VM", command=self.create_vm)
        create_button.pack(padx=10)
        
        # Progress and output
        output_frame = ttk.LabelFrame(form_frame, text="Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(output_frame, variable=self.progress_var, 
                                       maximum=100, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Output text
        self.output_text = tk.Text(output_frame, height=10, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for output text
        scrollbar = ttk.Scrollbar(self.output_text, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)

    def browse_storage_path(self):
        """Open dialog to browse for storage path"""
        path = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        if path:
            self.storage_path_var.set(path)
    
    def update_progress(self, value):
        """Update progress bar value"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def append_output(self, text):
        """Append text to output box"""
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def create_vm(self):
        """Handle VM creation process"""
        # Get form values
        ram_size = self.ram_size_var.get().strip()
        cpu_cores = self.cpu_cores_var.get().strip()
        disk_size = self.disk_size_var.get().strip()
        disk_format = self.disk_format_var.get()
        storage_path = self.storage_path_var.get()
        disk_name = self.disk_name_var.get().strip()
        
        # Validate inputs
        try:
            # Validate RAM
            ram_size = int(ram_size)
            if ram_size <= 0:
                raise ValueError("RAM size must be positive")
                
            # Validate CPU cores
            cpu_cores = int(cpu_cores)
            if cpu_cores <= 0:
                raise ValueError("CPU cores must be positive")
            
            # Validate disk size
            disk_size = int(disk_size)
            if disk_size <= 0:
                raise ValueError("Disk size must be positive")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        
        if not disk_name:
            messagebox.showerror("Invalid Input", "Please enter a disk name.")
            return
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(storage_path):
            try:
                os.makedirs(storage_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create storage directory: {e}")
                return
        
        # Start VM creation in a separate thread
        threading.Thread(target=self.create_vm_thread, 
                        args=(disk_size, disk_format, storage_path, disk_name)).start()
    
    def create_vm_thread(self, disk_size, disk_format, storage_path, disk_name):
        """Execute VM creation in a separate thread"""
        ram_size = int(self.ram_size_var.get().strip())
        cpu_cores = int(self.cpu_cores_var.get().strip())
        
        self.status_var.set("Creating virtual disk...")
        self.append_output(f"VM Configuration Summary:")
        self.append_output(f"  - RAM: {ram_size} GB")
        self.append_output(f"  - CPU Cores: {cpu_cores}")
        self.append_output(f"  - Disk: {disk_size} GB ({disk_format})")
        self.append_output(f"Creating {disk_size}GB {disk_format} disk...")
        self.update_progress(10)
        
        # Construct full disk path
        disk_path = os.path.join(storage_path, f"{disk_name}.{disk_format}")
        
        # Construct qemu-img command
        cmd = [
            "qemu-img", "create",
            "-f", disk_format,
            disk_path,
            f"{disk_size}G"
        ]
        
        self.append_output(f"Executing: {' '.join(cmd)}")
        self.update_progress(30)
        
        try:
            # Execute qemu-img command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            self.update_progress(60)
            
            if process.returncode == 0:
                self.append_output("Virtual disk created successfully!")
                self.append_output(f"Disk location: {disk_path}")
                
                # Now run the VM with qemu-system-x86_64
                self.status_var.set("Starting virtual machine...")
                self.append_output("Starting virtual machine...")
                
                # Convert RAM from GB to MB
                ram_mb = ram_size * 1024
                
                # Construct qemu-system command
                qemu_cmd = [
                    "qemu-system-x86_64",
                    "-hda", disk_path,
                    "-boot", "d",
                    "-m", str(ram_mb),
                    "-smp", str(cpu_cores)
                ]
                
                self.append_output(f"Executing: {' '.join(qemu_cmd)}")
                self.update_progress(80)
                
                # Create a bat file to run the command in MSYS2 MINGW64
                bat_path = os.path.join(storage_path, f"run_{disk_name}.bat")
                
                with open(bat_path, 'w') as f:
                    f.write("@echo off\n")
                    f.write("echo Starting QEMU emulator...\n")
                    f.write(f"start \"\" C:\\msys64\\mingw64.exe {' '.join(qemu_cmd)}\n")
                
                self.append_output(f"Created batch file: {bat_path}")
                self.append_output(f"You can run the VM by executing this batch file.")
                
                # Execute the batch file
                try:
                    subprocess.Popen(
                        ["cmd", "/c", bat_path],
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                    self.append_output("VM startup initiated!")
                except Exception as e:
                    self.append_output(f"Error starting VM: {str(e)}")
                    
                messagebox.showinfo("Success", "Virtual disk created and VM started!")
                self.status_var.set("VM running")
            else:
                self.append_output(f"Error creating disk: {stderr}")
                messagebox.showerror("Error", f"Failed to create virtual disk: {stderr}")
                self.status_var.set("Error creating VM disk")
                
            if stdout:
                self.append_output(f"Output: {stdout}")
                
        except Exception as e:
            self.append_output(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error")
            
        self.update_progress(100)

if __name__ == "__main__":
    root = tk.Tk()
    app = CloudManagementSystem(root)
    root.mainloop()