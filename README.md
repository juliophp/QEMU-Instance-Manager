## Installing SIM-PIPE

First thing to do is to install SIM-PIPE, for instructions visit https://github.com/DataCloud-project/SIM-PIPE

## Installing QEMU/libvirt/KVM

Installing QEMU on our host machine is the next step in setting up our QEMU Instance Manager. QEMU is a tool that can create emulated nodes, and it is required if we want to integrate an emulator into SIM-PIPE. 
As discussed in the tools section of our implementation, 
QEMU doesn't work alone; it works in collaboration with both KVM and libvirt. 
This is why all three of these tools must be installed simultaneously.

Run the following command to install QEMU, KVM, and libvirt:

```bash
sudo apt install qemu-kvm libvirt-clients libvirt-daemon-system 
bridge-utils virtinst libvirt-daemon
```
## Solving the Problem with `virsh` Permissions
By default, virsh doesn't allow sudo permissions, so we must first make it possible
for virsh to let us use the command without password. 
To solve this problem, there are three things that need to be done:
1. **Create a rule to allow using the libvirt command without supplying passwords**  
  Create a file at `/etc/polkit-1/rules.d/50-libvirt.rules` and add the following content to it:

   ```bash
   #!/bin/bash
   /* Allow users in wheel group to manage the libvirt
   daemon without authentication */
   polkit.addRule(function(action, subject) {
       if (action.id == "org.libvirt.unix.manage" &&
           subject.isInGroup("admin")) {
           return polkit.Result.YES;
       }
   });
```
 
2. **Open the libvirt configuration file**  
Uncomment the `uri_default` line. The path to the file is `/etc/libvirt/libvirt.conf`. Use the following command to modify the file:
```bash
   #!/bin/bash
   # These can be used in cases when no URI is supplied by the application
   # (@uri_default also prevents probing of the hypervisor driver).
   #
   uri_default = "qemu:///system"
```
3. **Copy the file into your user configuration directory**
   Run the command below to copy the file.
```bash
   #!/bin/bash
   sudo cp -rv /etc/libvirt/libvirt.conf ~/.config/libvirt/ &&
   sudo chown admin:admin ~/.config/libvirt/libvirt.conf
```
 After copying, give it the correct ownership. The following command will do this (in my case, `admin:admin` represents both my username and group name)
To test that it works, we can do a `virsh list --all` command. we should see an empty table, since we are yet to create any instance.

To be able to connect to our created instance through ssh, we must add our public key and name into this cloudconfig yml file

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


When creating a disk image for the operating system, we need a `base.img` file, which is required for this command to function. The `base.img` file represents the base image of the operating system that we plan to install on our emulated instance. 

The command to download the base image is shown below.

```bash
#!/bin/bash
wget -O base.img https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img
```
 ## Create Emulated Node

Once we have downloaded the base image, we can then run the create command.
```bash
python3 create.py --name controller --cpu 2 --memory 2048
```

 ## Removal or Delete Node
```bash
python3 remove.py --name controller
```
