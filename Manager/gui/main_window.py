"""
Main GUI window for HoUer Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import logging
from typing import List, Dict, Any

from .container_dialog import ContainerCreateDialog, ContainerSettingsDialog, ApplicationListDialog
from core.container_manager import Container

class HoUerManagerGUI:
    """Main GUI class for HoUer Manager"""
    
    def __init__(self, root, container_manager, config):
        self.root = root
        self.container_manager = container_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.containers = []
        self.selected_container = None
        
        self.setup_ui()
        self.refresh_containers()
        
        # Auto-refresh if enabled
        if self.config.get('auto_refresh', True):
            self.auto_refresh()
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.root.title("HoUer Manager - Container Management")
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create toolbar
        self.create_toolbar(main_frame)
        
        # Create container list
        self.create_container_list(main_frame)
        
        # Create status bar
        self.create_status_bar()
    
    def create_toolbar(self, parent):
        """Create the toolbar with action buttons"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side buttons
        left_frame = ttk.Frame(toolbar_frame)
        left_frame.pack(side=tk.LEFT)
        
        ttk.Button(
            left_frame,
            text="Create Container",
            command=self.create_container_dialog
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            left_frame,
            text="Refresh",
            command=self.refresh_containers
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            left_frame,
            text="Install from ISO",
            command=self.install_from_iso_dialog
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Right side buttons
        right_frame = ttk.Frame(toolbar_frame)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            right_frame,
            text="Settings",
            command=self.open_settings
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            right_frame,
            text="About",
            command=self.show_about
        ).pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_container_list(self, parent):
        """Create the container list with treeview"""
        # Container list frame
        list_frame = ttk.LabelFrame(parent, text="Containers")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('Name', 'Status', 'Distro', 'Type', 'Image')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_container_select)
        self.tree.bind('<Double-1>', self.on_container_double_click)
        
        # Context menu
        self.create_context_menu()
    
    def create_context_menu(self):
        """Create context menu for container list"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Start", command=self.start_container)
        self.context_menu.add_command(label="Stop", command=self.stop_container)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Settings", command=self.container_settings)
        self.context_menu.add_command(label="Applications", command=self.show_applications)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.delete_container)
        
        # Bind right-click
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def create_status_bar(self):
        """Create status bar at the bottom"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def refresh_containers(self):
        """Refresh the container list"""
        self.update_status("Refreshing container list...")
        
        def refresh_thread():
            try:
                self.containers = self.container_manager.get_containers()
                self.root.after(0, self.update_container_list)
            except Exception as e:
                self.logger.error(f"Error refreshing containers: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to refresh containers:\n{e}"))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def update_container_list(self):
        """Update the container list display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add containers
        for container in self.containers:
            # Color code by status
            tags = []
            if container.status == 'running':
                tags = ['running']
            elif container.status == 'stopped':
                tags = ['stopped']
            
            self.tree.insert('', tk.END, values=(
                container.name,
                container.status,
                container.distro,
                container.container_type,
                container.image
            ), tags=tags)
        
        # Configure tags
        self.tree.tag_configure('running', background='lightgreen')
        self.tree.tag_configure('stopped', background='lightcoral')
        
        self.update_status(f"Found {len(self.containers)} containers")
    
    def sort_by_column(self, col):
        """Sort container list by column"""
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        data.sort()
        
        for index, (val, item) in enumerate(data):
            self.tree.move(item, '', index)
    
    def on_container_select(self, event):
        """Handle container selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            
            # Find the selected container
            container_name = values[0]
            self.selected_container = next(
                (c for c in self.containers if c.name == container_name), 
                None
            )
    
    def on_container_double_click(self, event):
        """Handle double-click on container"""
        if self.selected_container:
            self.start_container()
    
    def show_context_menu(self, event):
        """Show context menu"""
        if self.tree.selection():
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
    
    def create_container_dialog(self):
        """Open create container dialog"""
        dialog = ContainerCreateDialog(self.root, self.container_manager, self.config)
        if dialog.result:
            self.refresh_containers()
    
    def start_container(self):
        """Start selected container"""
        if not self.selected_container:
            messagebox.showwarning("No Selection", "Please select a container first.")
            return
        
        self.update_status(f"Starting {self.selected_container.name}...")
        
        def start_thread():
            success = self.container_manager.start_container(self.selected_container)
            self.root.after(0, lambda: self.on_action_complete("start", success))
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def stop_container(self):
        """Stop selected container"""
        if not self.selected_container:
            messagebox.showwarning("No Selection", "Please select a container first.")
            return
        
        self.update_status(f"Stopping {self.selected_container.name}...")
        
        def stop_thread():
            success = self.container_manager.stop_container(self.selected_container)
            self.root.after(0, lambda: self.on_action_complete("stop", success))
        
        threading.Thread(target=stop_thread, daemon=True).start()
    
    def delete_container(self):
        """Delete selected container"""
        if not self.selected_container:
            messagebox.showwarning("No Selection", "Please select a container first.")
            return
        
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_container.name}'?\n"
            "This action cannot be undone."
        ):
            self.update_status(f"Deleting {self.selected_container.name}...")
            
            def delete_thread():
                success = self.container_manager.delete_container(self.selected_container)
                self.root.after(0, lambda: self.on_action_complete("delete", success))
            
            threading.Thread(target=delete_thread, daemon=True).start()
    
    def container_settings(self):
        """Open container settings dialog"""
        if not self.selected_container:
            messagebox.showwarning("No Selection", "Please select a container first.")
            return
        
        dialog = ContainerSettingsDialog(
            self.root, 
            self.selected_container, 
            self.container_manager, 
            self.config
        )
    
    def show_applications(self):
        """Show applications in selected container"""
        if not self.selected_container:
            messagebox.showwarning("No Selection", "Please select a container first.")
            return
        
        dialog = ApplicationListDialog(
            self.root,
            self.selected_container,
            self.container_manager
        )
    
    def install_from_iso_dialog(self):
        """Open install from ISO dialog"""
        iso_file = filedialog.askopenfilename(
            title="Select ISO File",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
        )
        
        if iso_file:
            container_name = tk.simpledialog.askstring(
                "Container Name",
                "Enter a name for the new container:"
            )
            
            if container_name:
                self.update_status(f"Installing from ISO: {iso_file}")
                
                def install_thread():
                    success = self.container_manager.install_from_iso(iso_file, container_name)
                    self.root.after(0, lambda: self.on_action_complete("install", success))
                
                threading.Thread(target=install_thread, daemon=True).start()
    
    def on_action_complete(self, action, success):
        """Handle completion of container actions"""
        if success:
            self.update_status(f"Container {action} completed successfully")
            self.refresh_containers()
        else:
            self.update_status(f"Container {action} failed")
            messagebox.showerror("Error", f"Failed to {action} container")
    
    def open_settings(self):
        """Open application settings"""
        messagebox.showinfo("Settings", "Settings dialog not implemented yet")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
HoUer Manager v1.0

Container Management for HoUer OS

Features:
• Linux container management via distrobox
• Windows container support via soda
• Application shortcut creation
• ISO installation support

Built with Python and Tkinter
        """
        messagebox.showinfo("About HoUer Manager", about_text.strip())
    
    def auto_refresh(self):
        """Auto-refresh containers periodically"""
        if self.config.get('auto_refresh', True):
            interval = self.config.get('refresh_interval', 5000)
            self.root.after(interval, lambda: [self.refresh_containers(), self.auto_refresh()]) 