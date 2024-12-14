## Installing SIM-PIPE

Now that we have SIM-PIPE cloned locally on our virtual machine, we will navigate into the SIM-PIPE folder and try to install SIM-PIPE using the install command.


## Installing QEMU/libvirt/KVM

Installing QEMU on our host machine is the next step in setting up our experiment. QEMU is a tool that can create emulated nodes, and it is required if we want to integrate an emulator into SIM-PIPE. As discussed in the tools section of our implementation, QEMU doesn't work alone; it works in collaboration with both KVM and libvirt. This is why all three of these tools must be installed simultaneously.

Run the following command to install QEMU, KVM, and libvirt:

```bash
sudo apt install qemu-kvm libvirt-clients libvirt-daemon-system 
bridge-utils virtinst libvirt-daemon
```
## Solving the Problem with `virsh` Permissions

To solve this problem, there are three things that need to be done:

1. **Open the libvirt configuration file**  
   Uncomment the `uri_default` line. The path to the file is `/etc/libvirt/libvirt.conf`. Use the following command to modify the file:

```bash
   #!/bin/bash
   # These can be used in cases when no URI is supplied by the application
   # (@uri_default also prevents probing of the hypervisor driver).
   #
   uri_default = "qemu:///system"
```
2. **Copy the file into your user configuration directory**  
   After copying, give it the correct ownership. The following command will do this (in my case, `admin:admin` represents both my username and group name):

```bash
   #!/bin/bash
   sudo cp -rv /etc/libvirt/libvirt.conf ~/.config/libvirt/ &&
   sudo chown admin:admin ~/.config/libvirt/libvirt.conf
```

## Generate Configuration Image

Having a configuration image is an important prerequisite for creating an emulated node with QEMU. A configuration image consists primarily of two types of configurations:

1. **User Configuration**
2. **Cloud Init Configuration**

Both configurations require their own configuration file, which is typically in `.yaml` or `.yml` format. In our use case, the configuration image will help us package these configurations to be loaded into the emulated node.

### User Configuration

The user configuration file allows for customization that would otherwise need to be done manually. It includes properties such as `local-hostname` and `instance-id` to set the node parameters before its creation. Here is an example of a user configuration file:

```yaml
#userconfig
instance-id: ubuntu
local-hostname: ubuntu
manage_etc_hosts: true
```

## User and Cloud Configuration Files
As you can see from the YML file above, the user configuration file allows for customization that would have had to be done manually. These configurations are loaded as part of the parameters required in creating the emulated node. The user configuration allows you to set properties such as `local-hostname` and `instance-id` on the node before its creation.

### Cloud Configuration File
The second file required for creating the `ubuntu.iso` file is the cloud configuration file. The cloud configuration file is similar to the user configuration file but allows customization of more important parameters.

Here is an example of a cloud configuration file:

```yaml
#cloudconfig
users:
    - default
    - name: adeyemi
ssh_authorized_keys:
    - ssh-rsa AAAAB 
sudo: ["ALL=(ALL) NOPASSWD:ALL"]
groups: sudo
shell: /bin/bash
```
## Generate Disk Image from Base Image

Another file required by the `diskpath` argument of the `virt-install` command is an OS disk image file, which we will name `ubuntu.img`. This file will be a disk image of the operating system we plan to install on our emulator.

When creating a disk image for the operating system, we need a `base.img` file, which is required for this command to function. The `base.img` file represents the base image of the operating system that we plan to install. To obtain this base image, we need to navigate to the repository of the operating system we wish to install and select the version we would like to download. As specified in the command, we will be downloading an image in the `qcow2` format.

The command to download the base image is shown below. Once we have downloaded the base image, we can run the following command:

```bash
#!/bin/bash
wget -O base.img https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img
```

This command also help us to set a storage size for our emulated node. In this case, in the command above we set the storage size of the emulated node to be 40Gb, \textit{ubuntu.img} is the output of the command, after execution, the command should produce an \textit{ubuntu.img} file in the same directory.
The command for generating the disk image is shown below. 


   
