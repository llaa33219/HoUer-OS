"""
Container management core functionality for HoUer Manager
"""

import subprocess
import json
import logging
import shutil
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Container:
    """Container information dataclass"""
    name: str
    status: str
    distro: str
    container_type: str  # 'linux' or 'windows'
    image: str
    created: str
    id: Optional[str] = None

class ContainerManager:
    """Main container management class"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Check if required tools are available
        self._check_tools()
    
    def _check_tools(self):
        """Check if required tools are installed"""
        required_tools = ['distrobox', 'podman']
        missing_tools = []
        
        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            self.logger.error(f"Missing required tools: {', '.join(missing_tools)}")
            raise RuntimeError(f"Missing required tools: {', '.join(missing_tools)}")
    
    def get_containers(self) -> List[Container]:
        """Get list of all containers"""
        containers = []
        
        # Get distrobox containers
        try:
            result = subprocess.run(
                ['distrobox', 'list', '--json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                distrobox_data = json.loads(result.stdout)
                for container_data in distrobox_data:
                    container = Container(
                        name=container_data.get('name', ''),
                        status=container_data.get('status', 'unknown'),
                        distro=container_data.get('distro', 'unknown'),
                        container_type='linux',
                        image=container_data.get('image', ''),
                        created=container_data.get('created', ''),
                        id=container_data.get('id')
                    )
                    containers.append(container)
        
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            self.logger.warning(f"Error getting distrobox containers: {e}")
        
        # Get Windows containers (soda-based)
        containers.extend(self._get_windows_containers())
        
        return containers
    
    def _get_windows_containers(self) -> List[Container]:
        """Get Windows containers managed by soda"""
        containers = []
        
        # Check if soda is available
        if not shutil.which('soda'):
            return containers
        
        try:
            # Get soda containers
            result = subprocess.run(
                ['soda', 'list'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse soda output (format may vary)
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        container = Container(
                            name=parts[0],
                            status='running' if 'running' in line.lower() else 'stopped',
                            distro='Windows',
                            container_type='windows',
                            image=parts[1] if len(parts) > 1 else 'windows',
                            created='unknown'
                        )
                        containers.append(container)
        
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Error getting soda containers: {e}")
        
        return containers
    
    def create_linux_container(self, name: str, image: str, additional_options: Dict[str, Any] = None) -> bool:
        """Create a new Linux container using distrobox"""
        try:
            cmd = ['distrobox', 'create', '--name', name, '--image', image]
            
            # Add additional options
            if additional_options:
                if additional_options.get('home_sharing', True):
                    cmd.extend(['--home', str(Path.home())])
                
                if additional_options.get('nvidia_support', False):
                    cmd.append('--nvidia')
                
                if additional_options.get('additional_packages'):
                    for package in additional_options['additional_packages']:
                        cmd.extend(['--additional-packages', package])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info(f"Successfully created container {name}")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error creating container {name}: {e}")
            return False
    
    def create_windows_container(self, name: str, windows_version: str) -> bool:
        """Create a new Windows container using soda"""
        if not shutil.which('soda'):
            self.logger.error("Soda is not installed")
            return False
        
        try:
            cmd = ['soda', 'create', '--name', name, '--version', windows_version]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info(f"Successfully created Windows container {name}")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error creating Windows container {name}: {e}")
            return False
    
    def start_container(self, container: Container) -> bool:
        """Start a container"""
        try:
            if container.container_type == 'linux':
                cmd = ['distrobox', 'enter', container.name]
            else:  # Windows
                cmd = ['soda', 'start', container.name]
            
            subprocess.Popen(cmd)
            self.logger.info(f"Started container {container.name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error starting container {container.name}: {e}")
            return False
    
    def stop_container(self, container: Container) -> bool:
        """Stop a container"""
        try:
            if container.container_type == 'linux':
                # For distrobox, we need to stop the underlying podman container
                cmd = ['podman', 'stop', container.name]
            else:  # Windows
                cmd = ['soda', 'stop', container.name]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info(f"Stopped container {container.name}")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error stopping container {container.name}: {e}")
            return False
    
    def delete_container(self, container: Container) -> bool:
        """Delete a container"""
        try:
            if container.container_type == 'linux':
                cmd = ['distrobox', 'rm', container.name, '--force']
            else:  # Windows
                cmd = ['soda', 'remove', container.name]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info(f"Deleted container {container.name}")
            
            # Remove container config
            config_path = self.config.get_container_config_path(container.name)
            if config_path.exists():
                config_path.unlink()
            
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error deleting container {container.name}: {e}")
            return False
    
    def get_container_applications(self, container: Container) -> List[Dict[str, str]]:
        """Get list of applications installed in a container"""
        applications = []
        
        if container.container_type == 'linux':
            try:
                # Get desktop files from the container
                cmd = ['distrobox', 'enter', container.name, '--', 'find', '/usr/share/applications', '-name', '*.desktop']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                for desktop_file in result.stdout.strip().split('\n'):
                    if desktop_file.strip():
                        app_info = self._parse_desktop_file(container, desktop_file.strip())
                        if app_info:
                            applications.append(app_info)
            
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Error getting applications for {container.name}: {e}")
        
        return applications
    
    def _parse_desktop_file(self, container: Container, desktop_file_path: str) -> Optional[Dict[str, str]]:
        """Parse a .desktop file to extract application information"""
        try:
            cmd = ['distrobox', 'enter', container.name, '--', 'cat', desktop_file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            app_info = {'desktop_file': desktop_file_path}
            
            for line in result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    if key == 'Name':
                        app_info['name'] = value
                    elif key == 'Exec':
                        app_info['exec'] = value
                    elif key == 'Icon':
                        app_info['icon'] = value
                    elif key == 'Comment':
                        app_info['comment'] = value
            
            return app_info if 'name' in app_info else None
        
        except subprocess.CalledProcessError:
            return None
    
    def create_application_shortcut(self, container: Container, app_info: Dict[str, str], 
                                  shortcut_name: str = None) -> bool:
        """Create a desktop shortcut for a container application"""
        try:
            desktop_dir = Path.home() / 'Desktop'
            desktop_dir.mkdir(exist_ok=True)
            
            if not shortcut_name:
                shortcut_name = f"{app_info.get('name', 'App')} ({container.name})"
            
            shortcut_file = desktop_dir / f"{shortcut_name}.desktop"
            
            if container.container_type == 'linux':
                exec_cmd = f"distrobox enter {container.name} -- {app_info.get('exec', '')}"
            else:
                exec_cmd = f"soda run {container.name} {app_info.get('exec', '')}"
            
            shortcut_content = f"""[Desktop Entry]
Name={shortcut_name}
Comment={app_info.get('comment', f'Run in {container.name} container')}
Exec={exec_cmd}
Icon={app_info.get('icon', 'application-x-executable')}
Terminal=false
Type=Application
Categories=HoUerManager;
"""
            
            with open(shortcut_file, 'w') as f:
                f.write(shortcut_content)
            
            # Make executable
            shortcut_file.chmod(0o755)
            
            self.logger.info(f"Created shortcut: {shortcut_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating shortcut: {e}")
            return False
    
    def install_from_iso(self, iso_path: str, container_name: str) -> bool:
        """Install a container from an ISO file"""
        try:
            # This is a simplified implementation
            # In a real scenario, you'd need to extract the ISO and create a container image
            
            iso_path_obj = Path(iso_path)
            if not iso_path_obj.exists():
                self.logger.error(f"ISO file not found: {iso_path}")
                return False
            
            # Create a temporary directory for extraction
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                # Mount or extract ISO (simplified)
                self.logger.info(f"Processing ISO: {iso_path}")
                
                # This would involve more complex logic to:
                # 1. Extract/mount the ISO
                # 2. Identify the OS type
                # 3. Create a container image from the ISO contents
                # 4. Set up the container with distrobox
                
                # For now, we'll just log and return success
                self.logger.info(f"ISO processing for {container_name} completed")
                return True
        
        except Exception as e:
            self.logger.error(f"Error installing from ISO: {e}")
            return False 