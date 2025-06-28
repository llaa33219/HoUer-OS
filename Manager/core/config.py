"""
Configuration management for HoUer Manager
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration manager for HoUer Manager"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.houer-manager'
        self.config_file = self.config_dir / 'config.json'
        self.containers_dir = self.config_dir / 'containers'
        
        # Create directories if they don't exist
        self.config_dir.mkdir(exist_ok=True)
        self.containers_dir.mkdir(exist_ok=True)
        
        self.default_config = {
            'theme': 'light',
            'auto_refresh': True,
            'refresh_interval': 5000,
            'container_storage_path': str(self.containers_dir),
            'supported_distros': {
                'linux': [
                    'ubuntu:latest',
                    'fedora:latest',
                    'debian:latest',
                    'archlinux:latest',
                    'alpine:latest',
                    'opensuse/tumbleweed:latest',
                    'centos:stream9'
                ],
                'windows': [
                    'windows-10',
                    'windows-11'
                ]
            },
            'distrobox_options': {
                'home_sharing': True,
                'nvidia_support': False,
                'audio_support': True,
                'additional_packages': []
            },
            'soda_options': {
                'dxvk_enabled': True,
                'vulkan_enabled': True,
                'audio_driver': 'pulseaudio'
            }
        }
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file.exists():
            self.save_config(self.default_config)
            return self.default_config.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Merge with default config to ensure all keys exist
            merged_config = self.default_config.copy()
            self._deep_update(merged_config, config)
            return merged_config
        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading config: {e}. Using default configuration.")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def _deep_update(self, base_dict: dict, update_dict: dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get_container_config_path(self, container_name: str) -> Path:
        """Get path to container-specific configuration"""
        return self.containers_dir / f"{container_name}.json"
    
    def save_container_config(self, container_name: str, config: Dict[str, Any]):
        """Save container-specific configuration"""
        config_path = self.get_container_config_path(container_name)
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving container config for {container_name}: {e}")
    
    def load_container_config(self, container_name: str) -> Dict[str, Any]:
        """Load container-specific configuration"""
        config_path = self.get_container_config_path(container_name)
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading container config for {container_name}: {e}")
            return {} 