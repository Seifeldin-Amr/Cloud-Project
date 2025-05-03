# Virtual Machine Manager

A modern GUI application for managing virtual machines using QEMU/KVM, built with Python and Kivy.

## Features

- **Virtual Disk Management**
  - Create virtual disks in various formats (qcow2, raw, vmdk, vhdx)
  - Manage existing virtual disks
  - Delete virtual disks

- **Virtual Machine Management**
  - Create new virtual machines with customizable settings
  - Manage existing virtual machines
  - Start/Stop virtual machines
  - Delete virtual machines

- **User Interface**
  - Modern and intuitive GUI built with Kivy
  - 3D animated intro screen
  - Easy-to-use forms for VM creation
  - Responsive design

## Prerequisites

- Python 3.x
- MSYS2 (for QEMU/KVM support)
- Required Python packages (install via pip):
  ```
  pip install kivy
  ```

## Installation

1. Install MSYS2 from [https://www.msys2.org/](https://www.msys2.org/)
2. Add MSYS2 to your system's PATH environment variable
3. Install QEMU/KVM through MSYS2:
   ```
   pacman -S mingw-w64-x86_64-qemu
   ```
4. Clone this repository
5. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python try.py
   ```

2. Main Menu Options:
   - **Create Virtual Disk**: Create a new virtual disk with specified format and size
   - **Manage Virtual Disks**: View and manage existing virtual disks
   - **Create Virtual Machine**: Create a new VM with custom settings
   - **Access Existing VMs**: View and manage existing virtual machines

3. Creating a Virtual Machine:
   - Enter VM name
   - Specify memory size (in GB)
   - Set number of CPU cores
   - Select an ISO file
   - Choose a virtual disk
   - Click "Create VM" to create the virtual machine

4. Managing Virtual Machines:
   - View list of existing VMs
   - Start/Stop VMs
   - Delete VMs
   - Refresh the VM list

## Directory Structure

- `try.py`: Main application file
- `README.md`: This documentation file
- Virtual disks and VM configurations are stored in the MSYS2 home directory under `qemu-disks/`

## Technical Details

- Built using Kivy framework for cross-platform GUI
- Uses QEMU/KVM for virtualization
- Implements a screen-based navigation system
- Features error handling and user feedback
- Supports multiple virtual disk formats
- Implements 3D animation using Kivy's graphics capabilities

## Troubleshooting

1. **MSYS2 Not Found**
   - Ensure MSYS2 is installed
   - Verify MSYS2 is in your system's PATH
   - Check the installation path in the application

2. **QEMU Not Working**
   - Verify QEMU is installed through MSYS2
   - Check if the mingw64.exe is present in the MSYS2 directory

3. **Permission Issues**
   - Run the application with appropriate permissions
   - Ensure write access to the qemu-disks directory

