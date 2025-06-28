#!/usr/bin/env python3
"""
HoUer Manager - Container Management for HoUer OS
Main application entry point
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Defer tkinter import until needed

# GUI imports will be done at runtime to avoid early tkinter dependency

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path.home() / '.houer-manager' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'houer-manager.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Check if required dependencies are installed"""
    required_commands = ['distrobox', 'podman']
    missing = []
    
    for cmd in required_commands:
        import subprocess
        try:
            subprocess.run(['which', cmd], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing.append(cmd)
    
    if missing:
        messagebox.showerror(
            "Missing Dependencies",
            f"The following required commands are not installed:\n{', '.join(missing)}\n\n"
            "Please install them using your package manager."
        )
        return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    import subprocess
    
    required_commands = ['distrobox', 'podman']
    missing = []
    
    for cmd in required_commands:
        try:
            subprocess.run(['which', cmd], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing.append(cmd)
    
    if missing:
        print(f"Warning: The following required commands are not installed: {', '.join(missing)}")
        print("HoUer Manager may not function properly without these dependencies.")
        print("Install them using your package manager.")
        return True  # Don't exit, just warn
    
    return True

def parse_arguments():
    """Parse command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HoUer Manager - Container Management for HoUer OS")
    parser.add_argument("--background", "-b", action="store_true", 
                       help="Run in background mode (system tray)")
    parser.add_argument("--minimized", "-m", action="store_true",
                       help="Start minimized")
    parser.add_argument("--version", "-v", action="version", version="HoUer Manager 1.0")
    parser.add_argument("--config-dir", type=str,
                       help="Custom configuration directory")
    parser.add_argument("--debug", "-d", action="store_true",
                       help="Enable debug logging")
    
    return parser.parse_args()

def main():
    """Main application entry point"""
    args = parse_arguments()
    
    # Setup logging with debug level if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting HoUer Manager")
    
    if args.background:
        logger.info("Running in background mode")
        # For now, just exit - future implementation could add system tray
        print("Background mode not yet implemented")
        return
    
    # Import GUI modules only when needed
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        print("Error: tkinter is not available. Please install python-tk package.")
        print("On Arch Linux: sudo pacman -S tk")
        print("On Ubuntu/Debian: sudo apt install python3-tk")
        print("On Fedora: sudo dnf install python3-tkinter")
        sys.exit(1)
    
    # Import our modules
    from gui.main_window import HoUerManagerGUI
    from core.container_manager import ContainerManager
    from core.config import Config
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Create main application
        root = tk.Tk()
        root.title("HoUer Manager")
        root.geometry("1000x700")
        root.minsize(800, 600)
        
        # Start minimized if requested
        if args.minimized:
            root.iconify()
        
        # Set application icon
        icon_path = Path(__file__).parent / 'assets' / 'icon.png'
        if icon_path.exists():
            try:
                icon = tk.PhotoImage(file=str(icon_path))
                root.iconphoto(True, icon)
            except Exception as e:
                logger.warning(f"Could not load icon: {e}")
        
        # Initialize configuration
        config = Config()
        
        # Use custom config directory if provided
        if args.config_dir:
            config.config_dir = Path(args.config_dir)
            config.config_file = config.config_dir / 'config.json'
            config.containers_dir = config.config_dir / 'containers'
            config.config_dir.mkdir(parents=True, exist_ok=True)
            config.containers_dir.mkdir(parents=True, exist_ok=True)
            config.config = config.load_config()
        
        # Initialize container manager
        container_manager = ContainerManager(config)
        
        # Create main GUI
        app = HoUerManagerGUI(root, container_manager, config)
        
        # Start the application
        logger.info("HoUer Manager GUI started")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Error starting HoUer Manager: {e}")
        try:
            messagebox.showerror("Error", f"Failed to start HoUer Manager:\n{e}")
        except:
            print(f"Failed to start HoUer Manager: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 