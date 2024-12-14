import argparse
import re
import subprocess
import yaml
import time
import sys


class CloudConfig:
    def __init__(self, hostname, manage_etc_hosts):
        self.instance_id = hostname
        self.hostname = hostname
        self.manage_etc_hosts = manage_etc_hosts

    def to_dict(self):
        return {
            "instance-id": self.hostname,
            "local-hostname": self.hostname,
            "manage_etc_hosts": self.manage_etc_hosts
        }

    def to_yaml(self, file_path):
        with open(file_path, 'w') as file:
            yaml.dump(self.to_dict(), file)

    @classmethod
    def from_yaml(cls, file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return cls(**data)

def show_loading(seconds):
    """Display a loading message for a given number of seconds."""
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rLoading... Please wait {remaining} seconds")
        sys.stdout.flush()
        time.sleep(1)
    print("\n")  # New line after loading


def get_ip_addresses(hostname):
    """Get IP addresses associated with the specified hostname from virsh DHCP leases."""
    try:
        # Run the command
        result = subprocess.run(
            ["virsh", "net-dhcp-leases", "default"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Check if the command ran successfully
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return

        # Extract lines with the specified hostname and parse IP addresses
        output = result.stdout
        lines_with_hostname = [
            line for line in output.splitlines() if hostname in line
        ]
        ip_addresses = []
        for line in lines_with_hostname:
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            if match:
                return match.group(1)

        return "Instance created but unable to obtain IP Address"

    except Exception as e:
        print(f"An error occurred: {e}")
def main(memory, name, cpu_count):
    try:

        # Create an instance of the CloudConfig class
        cloud_config = CloudConfig(hostname=name, manage_etc_hosts=True)

        # Define the file path for the YAML file
        cloud_config.to_yaml(f"{name}.yml")

        # Command 1: cloud-localds
        cloud_localds_command = ["cloud-localds", "-v", f"{name}.iso", "user-data.yaml", f"{name}.yml"]
        subprocess.run(cloud_localds_command, check=True)

        # Command 2: qemu-img create
        qemu_img_command = ["qemu-img", "create", "-b", "base.img", "-f", "qcow2", "-F", "qcow2", f"{name}.img", "40G"]
        subprocess.run(qemu_img_command, check=True)

        # Command 3: virt-install
        virt_install_command = [
            "virt-install",
            "--name", name,
            "--machine", "q35",
            "--cpu", "SandyBridge",
            "--accelerate",
            f"--vcpus={cpu_count}",
            "--memory", memory,
            "--os-type", "linux",
            "--os-variant", "ubuntu19.04",
            "--graphics", "none",
            "--network", "network=default,model=virtio",
            "--disk", f"path={name}.img,format=qcow2,device=disk,bus=virtio",
            "--disk", f"path={name}.iso,format=raw,device=disk,bus=virtio",
            "--noautoconsole",
            "--import"
        ]

        # Run virt-install command directly and capture its output
        result = subprocess.run(virt_install_command, universal_newlines=True)

        if result.returncode == 0:
            print("Command executed successfully.")
            print("Starting the process...")
            show_loading(30)  # Wait for 10 seconds with a loading message
            ip_addresses = get_ip_addresses(name)
            print("instance created: " + str({"hostname": name, "IP Address": ip_addresses}))
        else:
            print(f"Command failed with return code {result.returncode}")
            print(f"Error output:")
        # Save the output to a file for gawk processing

    except subprocess.CalledProcessError as e:
        # Handle errors during the execution of the command
        print(f"Command failed with return code {e.returncode}")
        print(f"Error output:\n{e.output}")

    except FileNotFoundError as e:
        print("Error: virsh is not installed or not in PATH.")
        print(str(e))

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to set up a virtual machine.")
    parser.add_argument("--memory", help="Amount of memory for the virtual machine.", required=True)
    parser.add_argument("--name", help="Name of the virtual machine.", required=True)
    parser.add_argument("--cpu-count", help="Number of CPUs for the virtual machine.", required=True)

    args = parser.parse_args()

    main(args.memory, args.name, args.cpu_count)
