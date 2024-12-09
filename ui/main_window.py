from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QLabel, QPushButton, QStackedWidget, QScrollArea)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from .widgets.dashboard import DashboardWidget
from .widgets.todo import TodoWidget
from .widgets.chat import ChatWidget
from .widgets.timetracker import TimeTrackerWidget
from .widgets.calendar import CalendarWidget
from .widgets.files import FilesWidget
from .widgets.profile_dialog import ProfileDialog
import os

class MainWindow(QMainWindow):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.setup_ui()
        self.load_style()
        self.showMaximized()

    def setup_ui(self):
        self.setWindowTitle("Gaming Business Software")
        
        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Sidebar header
        header = QLabel("Gaming Business Software")
        header.setObjectName("sidebarHeader")
        header.setContentsMargins(16, 16, 16, 16)
        sidebar_layout.addWidget(header)
        
        # Version numbers
        versions = ["v1.4.0", "v1.5.0", "v1.6.0", "v1.7.0", "v1.8.0"]
        for version in versions:
            version_btn = QPushButton(version)
            version_btn.setObjectName("sidebarItem")
            sidebar_layout.addWidget(version_btn)
        
        # Project Management section
        project_header = QLabel("Project Management")
        project_header.setObjectName("sidebarHeader")
        project_header.setContentsMargins(16, 16, 16, 8)
        sidebar_layout.addWidget(project_header)
        
        # Add Project button
        add_project_btn = QPushButton("+ Add Project")
        add_project_btn.setObjectName("addProjectButton")
        add_project_btn.setContentsMargins(16, 8, 16, 8)
        sidebar_layout.addWidget(add_project_btn)
        
        # Project list
        project_scroll = QScrollArea()
        project_scroll.setWidgetResizable(True)
        project_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        project_widget = QWidget()
        self.project_layout = QVBoxLayout(project_widget)
        self.project_layout.setContentsMargins(8, 8, 8, 8)
        self.project_layout.setSpacing(4)
        project_scroll.setWidget(project_widget)
        sidebar_layout.addWidget(project_scroll)
        
        # Load projects
        projects = self.db_manager.get_projects(self.user_data["id"])
        for project in projects:
            project_btn = QPushButton(f"{project['name']} ({project['todo_count']})")
            project_btn.setObjectName("sidebarItem")
            self.project_layout.addWidget(project_btn)
        
        self.project_layout.addStretch()
        
        # Add sidebar to main layout
        main_layout.addWidget(sidebar)
        
        # Content area
        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("main-tabs")

        # Create tab widgets
        self.tab_widgets = {
            "dashboard": DashboardWidget(self.db_manager, self.user_data),
            "todo": TodoWidget(self.db_manager, self.user_data),
            "chat": ChatWidget(self.db_manager, self.user_data),
            "timetracker": TimeTrackerWidget(self.db_manager, self.user_data),
            "calendar": CalendarWidget(self.db_manager, self.user_data),
            "files": FilesWidget(self.db_manager, self.user_data)
        }

        # Add tabs
        tab_info = {
            "dashboard": "Dashboard",
            "todo": "Todo",
            "chat": "Chat",
            "timetracker": "Time Tracker",
            "calendar": "Calendar",
            "files": "Files"
        }

        for key, title in tab_info.items():
            self.tabs.addTab(self.tab_widgets[key], title)

        content_layout.addWidget(self.tabs)

        # Add content to main layout
        main_layout.addWidget(content)

    def load_style(self):
        style_path = os.path.join(os.path.dirname(__file__), 'style.qss')
        with open(style_path, 'r') as f:
            self.setStyleSheet(f.read())

    def switch_to_tab(self, tab_name):
        if tab_name in self.tab_widgets:
            self.tabs.setCurrentWidget(self.tab_widgets[tab_name])
            
    def show_profile(self, event):
        dialog = ProfileDialog(self.user_data, self.db_manager, self)
        dialog.exec_()
