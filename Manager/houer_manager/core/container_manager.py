import subprocess

class ContainerManager:
    def __init__(self):
        pass

    def list_containers(self):
        # This is a placeholder. We will implement this to call 'distrobox list'
        # and parse the output.
        print("Listing containers...")
        # For now, return some dummy data
        return [
            {"name": "arch-linux", "status": "Running", "os": "arch"},
            {"name": "ubuntu-22.04", "status": "Stopped", "os": "ubuntu"},
            {"name": "MyWindows", "status": "Running", "os": "windows"},
        ] 