import argparse
import subprocess
import sys

# Function to run a shell command and print the output, without stopping execution on failure
def run_command(command, ignore_failure=True):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if not ignore_failure:
            sys.exit(1)

# Main function
def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Drain, delete, and clean up a Kubernetes node.")
    parser.add_argument("--name", required=True, help="Name of the node to drain, delete, and clean up.")
    args = parser.parse_args()

    # Extract the node name
    node_name = args.name

    # Drain the node using kubectl
    print(f"Draining node {node_name}...")
    run_command(f"kubectl drain {node_name} --ignore-daemonsets --delete-local-data --force")

    # Delete the node from Kubernetes
    print(f"Deleting node {node_name} from Kubernetes...")
    run_command(f"kubectl delete node {node_name}")

    # Undefine and destroy the VM using virsh
    print(f"Undefining and destroying the VM {node_name}...")
    run_command(f"virsh undefine {node_name}")
    run_command(f"virsh destroy {node_name}")

    # Remove any controller-related files
    print("Removing node files...")
    run_command(f"sudo rm {node_name}*")

    # Print the completion message
    print("Completed.")

# Run the script
if __name__ == "__main__":
    main()
