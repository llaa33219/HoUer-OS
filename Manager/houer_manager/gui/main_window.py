import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QListWidget, QListWidgetItem, QLabel, QPushButton, QHBoxLayout, QToolBar
)
from PyQt6.QtGui import QIcon, QAction
from ..core.container_manager import ContainerManager

class ContainerItemWidget(QWidget):
    def __init__(self, container_info):
        super().__init__()
        self.container_info = container_info
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # OS Logo (placeholder)
        logo_label = QLabel("Icon") # Placeholder, we'll use an icon later
        layout.addWidget(logo_label)

        # Name and Status
        name_status_layout = QVBoxLayout()
        name_label = QLabel(self.container_info.get("name", "N/A"))
        name_label.setStyleSheet("font-weight: bold;")
        status_label = QLabel(f"Status: {self.container_info.get('status', 'N/A')}")
        name_status_layout.addWidget(name_label)
        name_status_layout.addWidget(status_label)
        layout.addLayout(name_status_layout)

        layout.addStretch()

        # Action Buttons
        btn_run = QPushButton("Start")
        btn_stop = QPushButton("Stop")
        btn_delete = QPushButton("Delete")
        btn_settings = QPushButton("Settings")
        btn_apps = QPushButton("Apps")

        layout.addWidget(btn_run)
        layout.addWidget(btn_stop)
        layout.addWidget(btn_delete)
        layout.addWidget(btn_settings)
        layout.addWidget(btn_apps)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HoUer Manager")
        self.setGeometry(100, 100, 800, 600)

        self.container_manager = ContainerManager()

        self.init_ui()
        self.refresh_container_list()

    def init_ui(self):
        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        create_action = QAction(QIcon(), "Create Container", self)
        # create_action.triggered.connect(self.create_container_dialog) # To be implemented
        toolbar.addAction(create_action)

        refresh_action = QAction(QIcon(), "Refresh", self)
        refresh_action.triggered.connect(self.refresh_container_list)
        toolbar.addAction(refresh_action)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.container_list = QListWidget()
        layout.addWidget(self.container_list)

    def refresh_container_list(self):
        self.container_list.clear()
        containers = self.container_manager.list_containers()
        for container in containers:
            item_widget = ContainerItemWidget(container)
            list_item = QListWidgetItem(self.container_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.container_list.addItem(list_item)
            self.container_list.setItemWidget(list_item, item_widget) 