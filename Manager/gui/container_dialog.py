"""
Dialog windows for container operations
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import logging
from typing import List, Dict, Any, Optional

class ContainerCreateDialog:
    """Dialog for creating new containers"""
    
    def __init__(self, parent, container_manager, config):
        self.parent = parent
        self.container_manager = container_manager
        self.config = config
        self.result = None
        self.logger = logging.getLogger(__name__)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Container")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.center_dialog()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Container type selection
        type_frame = ttk.LabelFrame(main_frame, text="Container Type")
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.container_type = tk.StringVar(value="linux")
        ttk.Radiobutton(
            type_frame, 
            text="Linux Container", 
            variable=self.container_type, 
            value="linux",
            command=self.on_type_changed
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Radiobutton(
            type_frame, 
            text="Windows Container", 
            variable=self.container_type, 
            value="windows",
            command=self.on_type_changed
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Container details
        details_frame = ttk.LabelFrame(main_frame, text="Container Details")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Name
        ttk.Label(details_frame, text="Container Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        # Image/Version selection
        self.image_label = ttk.Label(details_frame, text="Distribution:")
        self.image_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.image_var = tk.StringVar()
        self.image_combo = ttk.Combobox(details_frame, textvariable=self.image_var, width=37, state="readonly")
        self.image_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Options frame
        self.options_frame = ttk.LabelFrame(main_frame, text="Options")
        self.options_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Linux options
        self.linux_options_frame = ttk.Frame(self.options_frame)
        
        self.home_sharing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.linux_options_frame,
            text="Share home directory",
            variable=self.home_sharing_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.nvidia_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.linux_options_frame,
            text="Enable NVIDIA support",
            variable=self.nvidia_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.audio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.linux_options_frame,
            text="Enable audio support",
            variable=self.audio_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Windows options
        self.windows_options_frame = ttk.Frame(self.options_frame)
        
        self.dxvk_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.windows_options_frame,
            text="Enable DXVK",
            variable=self.dxvk_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.vulkan_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.windows_options_frame,
            text="Enable Vulkan",
            variable=self.vulkan_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Create",
            command=self.create_container
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
        
        # Initialize UI state
        self.on_type_changed()
    
    def on_type_changed(self):
        """Handle container type change"""
        container_type = self.container_type.get()
        
        if container_type == "linux":
            self.image_label.config(text="Distribution:")
            self.image_combo['values'] = self.config.get('supported_distros.linux', [])
            self.linux_options_frame.pack(fill=tk.BOTH, expand=True)
            self.windows_options_frame.pack_forget()
        else:
            self.image_label.config(text="Windows Version:")
            self.image_combo['values'] = self.config.get('supported_distros.windows', [])
            self.windows_options_frame.pack(fill=tk.BOTH, expand=True)
            self.linux_options_frame.pack_forget()
        
        if self.image_combo['values']:
            self.image_var.set(self.image_combo['values'][0])
    
    def create_container(self):
        """Create the container"""
        name = self.name_var.get().strip()
        image = self.image_var.get()
        container_type = self.container_type.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter a container name.")
            return
        
        if not image:
            messagebox.showerror("Error", "Please select an image/version.")
            return
        
        # Disable create button
        self.dialog.config(cursor="wait")
        
        def create_thread():
            try:
                if container_type == "linux":
                    options = {
                        'home_sharing': self.home_sharing_var.get(),
                        'nvidia_support': self.nvidia_var.get(),
                        'audio_support': self.audio_var.get()
                    }
                    success = self.container_manager.create_linux_container(name, image, options)
                else:
                    success = self.container_manager.create_windows_container(name, image)
                
                self.dialog.after(0, lambda: self.on_create_complete(success))
            
            except Exception as e:
                self.logger.error(f"Error creating container: {e}")
                self.dialog.after(0, lambda: self.on_create_complete(False))
        
        threading.Thread(target=create_thread, daemon=True).start()
    
    def on_create_complete(self, success):
        """Handle creation completion"""
        self.dialog.config(cursor="")
        
        if success:
            self.result = True
            messagebox.showinfo("Success", "Container created successfully!")
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to create container.")
    
    def center_dialog(self):
        """Center the dialog on parent"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")

class ContainerSettingsDialog:
    """Dialog for container settings"""
    
    def __init__(self, parent, container, container_manager, config):
        self.parent = parent
        self.container = container
        self.container_manager = container_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Settings - {container.name}")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.center_dialog()
    
    def setup_ui(self):
        """Setup the settings dialog UI"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Container info
        info_frame = ttk.LabelFrame(main_frame, text="Container Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Name: {self.container.name}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Type: {self.container.container_type}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Status: {self.container.status}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Image: {self.container.image}").pack(anchor=tk.W, padx=5, pady=2)
        
        # Settings based on container type
        if self.container.container_type == "linux":
            self.setup_linux_settings(main_frame)
        else:
            self.setup_windows_settings(main_frame)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def setup_linux_settings(self, parent):
        """Setup Linux container settings"""
        settings_frame = ttk.LabelFrame(parent, text="Distrobox Settings")
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(
            settings_frame,
            text="Linux container settings would be managed\nthrough distrobox configuration files.",
            justify=tk.CENTER
        ).pack(expand=True)
    
    def setup_windows_settings(self, parent):
        """Setup Windows container settings"""
        settings_frame = ttk.LabelFrame(parent, text="Soda Settings")
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Button(
            settings_frame,
            text="Open Soda Configuration",
            command=self.open_soda_config
        ).pack(pady=20)
    
    def open_soda_config(self):
        """Open soda configuration for Windows container"""
        try:
            import subprocess
            subprocess.Popen(['soda', 'config', self.container.name])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open soda configuration:\n{e}")
    
    def center_dialog(self):
        """Center the dialog on parent"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")

class ApplicationListDialog:
    """Dialog for showing container applications"""
    
    def __init__(self, parent, container, container_manager):
        self.parent = parent
        self.container = container
        self.container_manager = container_manager
        self.logger = logging.getLogger(__name__)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Applications - {container.name}")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.applications = []
        self.selected_app = None
        
        self.setup_ui()
        self.center_dialog()
        self.load_applications()
    
    def setup_ui(self):
        """Setup the applications dialog UI"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Applications list
        list_frame = ttk.LabelFrame(main_frame, text="Installed Applications")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview
        columns = ('Name', 'Executable')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.tree.heading('Name', text='Application Name')
        self.tree.heading('Executable', text='Executable')
        
        self.tree.column('Name', width=200)
        self.tree.column('Executable', width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_app_select)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Create Shortcut",
            command=self.create_shortcut
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.load_applications
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def load_applications(self):
        """Load applications from container"""
        self.dialog.config(cursor="wait")
        
        def load_thread():
            try:
                self.applications = self.container_manager.get_container_applications(self.container)
                self.dialog.after(0, self.update_applications_list)
            except Exception as e:
                self.logger.error(f"Error loading applications: {e}")
                self.dialog.after(0, lambda: messagebox.showerror("Error", f"Failed to load applications:\n{e}"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def update_applications_list(self):
        """Update the applications list display"""
        self.dialog.config(cursor="")
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add applications
        for app in self.applications:
            self.tree.insert('', tk.END, values=(
                app.get('name', 'Unknown'),
                app.get('exec', 'Unknown')
            ))
    
    def on_app_select(self, event):
        """Handle application selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            app_name = values[0]
            
            self.selected_app = next(
                (app for app in self.applications if app.get('name') == app_name),
                None
            )
    
    def create_shortcut(self):
        """Create desktop shortcut for selected application"""
        if not self.selected_app:
            messagebox.showwarning("No Selection", "Please select an application first.")
            return
        
        shortcut_name = simpledialog.askstring(
            "Shortcut Name",
            f"Enter name for shortcut:\n(default: {self.selected_app.get('name', 'App')})",
            initialvalue=f"{self.selected_app.get('name', 'App')} ({self.container.name})"
        )
        
        if shortcut_name:
            success = self.container_manager.create_application_shortcut(
                self.container,
                self.selected_app,
                shortcut_name
            )
            
            if success:
                messagebox.showinfo("Success", "Desktop shortcut created successfully!")
            else:
                messagebox.showerror("Error", "Failed to create desktop shortcut.")
    
    def center_dialog(self):
        """Center the dialog on parent"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}") 