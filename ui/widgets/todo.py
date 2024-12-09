from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QLineEdit, QComboBox,
                               QDateTimeEdit, QScrollArea, QFrame, QTextEdit,
                               QMessageBox, QDialog, QGridLayout, QSpacerItem,
                               QSizePolicy, QListWidget, QListWidgetItem, QCompleter, QLayout, QCheckBox,
                               QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, Signal, QDateTime, QRect, QPoint, QSize
from PySide6.QtGui import QColor, QIcon
from datetime import datetime, timedelta
from itertools import groupby
from operator import itemgetter

class UserTag(QFrame):
    removed = Signal(str)  # Signal when tag is removed

    def __init__(self, username, user_id):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.setup_ui()
        
    def setup_ui(self):
        self.setObjectName("userTag")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        
        # User icon
        icon_label = QLabel("👤")
        icon_label.setObjectName("tagIcon")
        layout.addWidget(icon_label)
        
        # Username
        name_label = QLabel(self.username)
        name_label.setObjectName("tagText")
        layout.addWidget(name_label)
        
        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setObjectName("tagRemove")
        remove_btn.clicked.connect(lambda: self.removed.emit(self.user_id))
        layout.addWidget(remove_btn)
        
        self.setStyleSheet("""
            #userTag {
                background-color: #2c2c2c;
                border-radius: 12px;
                min-width: 80px;
                max-height: 24px;
            }
            #tagIcon {
                font-size: 12px;
                color: #cccccc;
            }
            #tagText {
                color: #cccccc;
                font-size: 12px;
            }
            #tagRemove {
                background: transparent;
                color: #cccccc;
                border: none;
                font-size: 14px;
                padding: 0;
                min-width: 16px;
            }
            #tagRemove:hover {
                color: #ffffff;
            }
        """)

class UserSearchComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setMaxVisibleItems(10)
        self.setStyleSheet("""
            QComboBox {
                background-color: #2c2c2c;
                border: 1px solid #363636;
                border-radius: 4px;
                color: #cccccc;
                font-size: 13px;
                padding: 4px 8px;
                height: 24px;
            }
            QComboBox:focus {
                border: 1px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2c2c2c;
                border: 1px solid #363636;
                color: #cccccc;
                selection-background-color: #3498db;
                selection-color: #ffffff;
            }
        """)

class AddTaskModal(QDialog):
    def __init__(self, db_manager, parent=None, user_data=None, task_data=None, project_id=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_data = user_data
        self.task_data = task_data
        self.project_id = project_id
        self.users = []
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container
        container = QFrame()
        container.setObjectName("modalContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Title bar
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setObjectName("titleBar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(16, 0, 8, 0)
        title_layout.setSpacing(8)
        
        # Title with icon
        title_icon = QLabel("✏️")
        title_icon.setObjectName("titleIcon")
        title_layout.addWidget(title_icon)
        
        if self.task_data:
            title_label = QLabel("Edit Task")
        else:
            title_label = QLabel("Create New Task")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        # Content
        content = QFrame()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 24)
        content_layout.setSpacing(16)
        
        # Task name with icon
        name_container = QFrame()
        name_container.setObjectName("inputContainer")
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(12, 0, 12, 0)
        name_layout.setSpacing(8)
        
        name_icon = QLabel("📝")
        name_icon.setObjectName("inputIcon")
        name_layout.addWidget(name_icon)
        
        self.name_input = QLineEdit()
        self.name_input.setObjectName("nameInput")
        self.name_input.setPlaceholderText("What needs to be done?")
        if self.task_data:
            self.name_input.setText(self.task_data.get("title", ""))
        name_layout.addWidget(self.name_input)
        
        # Description
        desc_container = QFrame()
        desc_container.setObjectName("inputContainer")
        desc_layout = QVBoxLayout(desc_container)
        desc_layout.setContentsMargins(12, 12, 12, 12)
        desc_layout.setSpacing(8)
        
        desc_header = QHBoxLayout()
        desc_icon = QLabel("📋")
        desc_icon.setObjectName("inputIcon")
        desc_header.addWidget(desc_icon)
        
        desc_label = QLabel("Description")
        desc_label.setObjectName("inputLabel")
        desc_header.addWidget(desc_label)
        desc_header.addStretch()
        
        self.desc_input = QTextEdit()
        self.desc_input.setObjectName("descInput")
        self.desc_input.setPlaceholderText("Add a more detailed description...")
        self.desc_input.setMinimumHeight(100)
        if self.task_data:
            self.desc_input.setText(self.task_data.get("description", ""))
        
        desc_layout.addLayout(desc_header)
        desc_layout.addWidget(self.desc_input)
        
        # Details row
        details = QHBoxLayout()
        details.setSpacing(16)
        
        # Priority
        priority_container = QFrame()
        priority_container.setObjectName("inputContainer")
        priority_layout = QHBoxLayout(priority_container)
        priority_layout.setContentsMargins(12, 0, 12, 0)
        priority_layout.setSpacing(8)
        
        priority_icon = QLabel("🎯")
        priority_icon.setObjectName("inputIcon")
        priority_layout.addWidget(priority_icon)
        
        self.priority_combo = QComboBox()
        self.priority_combo.setObjectName("priorityCombo")
        self.priority_combo.addItems(["Low", "Medium", "High", "Critical"])
        if self.task_data:
            self.priority_combo.setCurrentText(self.task_data.get("priority", "Medium"))
        else:
            self.priority_combo.setCurrentText("Medium")
        self.priority_combo.setFixedWidth(120)
        priority_layout.addWidget(self.priority_combo)
        
        # Deadline
        deadline_container = QFrame()
        deadline_container.setObjectName("inputContainer")
        deadline_layout = QHBoxLayout(deadline_container)
        deadline_layout.setContentsMargins(12, 0, 12, 0)
        deadline_layout.setSpacing(8)
        
        deadline_icon = QLabel("📅")
        deadline_icon.setObjectName("inputIcon")
        deadline_layout.addWidget(deadline_icon)
        
        self.deadline_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.deadline_edit.setObjectName("deadlineEdit")
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.deadline_edit.setMinimumDateTime(QDateTime.currentDateTime())
        self.deadline_edit.setFixedWidth(180)
        if self.task_data:
            self.deadline_edit.setDateTime(QDateTime.fromString(self.task_data.get("deadline", ""), Qt.ISODate))
        deadline_layout.addWidget(self.deadline_edit)
        
        details.addWidget(priority_container)
        details.addWidget(deadline_container)
        details.addStretch()
        
        # User assignment
        assign_container = QFrame()
        assign_container.setObjectName("inputContainer")
        assign_layout = QVBoxLayout(assign_container)
        assign_layout.setContentsMargins(12, 12, 12, 12)
        assign_layout.setSpacing(12)
        
        # Header
        assign_header = QHBoxLayout()
        assign_icon = QLabel("👥")
        assign_icon.setObjectName("inputIcon")
        assign_header.addWidget(assign_icon)
        
        assign_label = QLabel("Assign To")
        assign_label.setObjectName("inputLabel")
        assign_header.addWidget(assign_label)
        assign_header.addStretch()
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        self.user_combo = UserSearchComboBox()
        self.user_combo.setPlaceholderText("Search users...")
        self.user_combo.lineEdit().textChanged.connect(self.filter_users)
        self.user_combo.activated.connect(self.add_selected_user)
        search_layout.addWidget(self.user_combo)
        
        # Tags scroll area
        scroll = QScrollArea()
        scroll.setObjectName("tagsScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setMinimumHeight(80)
        scroll.setMaximumHeight(120)
        
        self.tags_container = QFrame()
        self.tags_container.setObjectName("tagsContainer")
        self.tags_layout = QFlowLayout(self.tags_container)
        self.tags_layout.setContentsMargins(4, 4, 4, 4)
        self.tags_layout.setSpacing(8)
        
        scroll.setWidget(self.tags_container)
        
        assign_layout.addLayout(assign_header)
        assign_layout.addLayout(search_layout)
        assign_layout.addWidget(scroll)
        
        # Buttons
        button_container = QWidget()
        button_container.setObjectName("buttonContainer")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.clicked.connect(self.reject)
        
        if self.task_data:
            create_btn = QPushButton("Update Task")
        else:
            create_btn = QPushButton("Create Task")
        create_btn.setObjectName("createButton")
        create_btn.setFixedSize(120, 36)
        create_btn.clicked.connect(self.create_task)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        
        # Add all to content
        content_layout.addWidget(name_container)
        content_layout.addWidget(desc_container)
        content_layout.addLayout(details)
        content_layout.addWidget(assign_container)
        content_layout.addStretch()
        content_layout.addWidget(button_container)
        
        # Add to container
        container_layout.addWidget(title_bar)
        container_layout.addWidget(content)
        
        # Add to main layout
        main_layout.addWidget(container)
        
        # Set size
        self.setFixedSize(700, 700)
        
        # Make window draggable
        self._drag_pos = None
        title_bar.mousePressEvent = self._get_drag_pos
        title_bar.mouseMoveEvent = self._handle_drag
        
        # Apply styles
        self.setStyleSheet("""
            #modalContainer {
                background-color: #2b2b2b;
                border: 1px solid #3f3f3f;
                border-radius: 8px;
            }
            
            #titleBar {
                background-color: #1e1e1e;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            
            #titleIcon {
                font-size: 16px;
            }
            
            #titleLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            
            #closeButton {
                background: transparent;
                border: none;
                color: #808080;
                font-size: 20px;
            }
            
            #closeButton:hover {
                background-color: #c42b1c;
                color: white;
            }
            
            #contentArea {
                background-color: #2b2b2c;
            }
            
            #inputContainer {
                background-color: #363636;
                border: 1px solid #3f3f3f;
                border-radius: 6px;
            }
            
            #inputIcon {
                font-size: 14px;
                min-width: 20px;
            }
            
            #inputLabel {
                color: #cccccc;
                font-size: 13px;
                font-weight: bold;
            }
            
            QLineEdit, QTextEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 13px;
                padding: 4px;
            }
            
            QLineEdit {
                height: 24px;
            }
            
            QComboBox {
                background-color: #404040;
                border: 1px solid #4f4f4f;
                border-radius: 4px;
                color: white;
                font-size: 13px;
                padding: 4px 8px;
                height: 24px;
            }
            
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            
            QComboBox QAbstractItemView {
                background-color: #404040;
                color: white;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            
            QDateTimeEdit {
                background-color: #404040;
                border: 1px solid #4f4f4f;
                border-radius: 4px;
                color: white;
                font-size: 13px;
                padding: 4px 8px;
                height: 24px;
            }
            
            QDateTimeEdit:focus {
                border: 1px solid #0078d4;
            }
            
            QDateTimeEdit::up-button, QDateTimeEdit::down-button {
                background: transparent;
                border: none;
            }
            
            #tagsScroll {
                background: transparent;
                border: none;
            }
            
            #tagsContainer {
                background: transparent;
            }
            
            #cancelButton {
                background-color: #404040;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 13px;
                font-weight: bold;
            }
            
            #cancelButton:hover {
                background-color: #4f4f4f;
            }
            
            #createButton {
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 13px;
                font-weight: bold;
            }
            
            #createButton:hover {
                background-color: #006cbd;
            }
            
            QScrollBar:vertical {
                background: #2b2b2b;
                width: 8px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background: #404040;
                min-height: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Load users
        self.load_users()
    
    def _get_drag_pos(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def _handle_drag(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    
    def load_users(self):
        """Load users from database"""
        self.users = self.db_manager.get_users()
        self.filter_users("")  # Show all users initially
    
    def filter_users(self, filter_text):
        """Filter users based on search text"""
        self.user_combo.clear()
        self.user_combo.addItem("Select User", None)  # Add default option
        
        users = self.db_manager.get_users()
        for user in users:
            username = user["username"]
            if filter_text.lower() in username.lower():
                self.user_combo.addItem(username, user["id"])
        
        # Show dropdown if there are matching users
        if self.user_combo.count() > 0:
            self.user_combo.showPopup()
    
    def add_selected_user(self, index):
        """Add selected user to the tags container"""
        if index < 0:
            return
            
        username = self.user_combo.currentText()
        user_id = self.user_combo.currentData()
        
        if not user_id:
            return
            
        # Check if user is already added
        for i in range(self.tags_layout.count()):
            item = self.tags_layout.itemAt(i)
            if item and isinstance(item.widget(), UserTag) and item.widget().user_id == user_id:
                return
        
        # Create and add new tag
        tag = UserTag(username, user_id)
        tag.removed.connect(self.remove_user)
        self.tags_layout.addWidget(tag)
        
        # Reset combo box
        self.user_combo.clearEditText()
        self.user_combo.clear()
    
    def remove_user(self, user_id):
        for i in range(self.tags_layout.count()):
            item = self.tags_layout.itemAt(i)
            if item and isinstance(item.widget(), UserTag) and item.widget().user_id == user_id:
                widget = item.widget()
                self.tags_layout.removeWidget(widget)
                widget.deleteLater()
                break
    
    def get_selected_users(self):
        user_ids = []
        for i in range(self.tags_layout.count()):
            item = self.tags_layout.itemAt(i)
            if item and isinstance(item.widget(), UserTag):
                user_ids.append(item.widget().user_id)
        return user_ids

    def create_task(self):
        """Create a new task"""
        title = self.name_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Error", "Title is required")
            return
            
        description = self.desc_input.toPlainText().strip()
        priority = self.priority_combo.currentText()
        deadline = self.deadline_edit.dateTime().toString(Qt.ISODate)
        assignees = self.get_selected_users()
        
        if self.task_data:
            try:
                task_id = self.db_manager.update_todo(
                    self.task_data["id"],
                    title=title,
                    description=description,
                    priority=priority,
                    deadline=deadline,
                    assignees=assignees
                )
                
                if task_id:
                    self.accept()  # Close dialog
                else:
                    QMessageBox.warning(self, "Error", "Failed to update task")
                    
            except Exception as e:
                print(f"Error updating task: {e}")
                QMessageBox.warning(self, "Error", f"Failed to update task: {str(e)}")
        else:
            try:
                task_id = self.db_manager.create_todo(
                    title=title,
                    description=description,
                    priority=priority,
                    deadline=deadline,
                    created_by=self.user_data["id"],
                    assignees=assignees,
                    project_id=self.project_id
                )
                
                if task_id:
                    self.accept()  # Close dialog
                else:
                    QMessageBox.warning(self, "Error", "Failed to create task")
                    
            except Exception as e:
                print(f"Error creating task: {e}")
                QMessageBox.warning(self, "Error", f"Failed to create task: {str(e)}")

class QFlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._rows = []  # List of rows, each row is a list of items
        self._spacing = 0
        
    def addItem(self, item):
        self._items.append(item)
        
    def count(self):
        return len(self._items)
        
    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
        
    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None
        
    def expandingDirections(self):
        return Qt.Orientations()
        
    def hasHeightForWidth(self):
        return True
        
    def heightForWidth(self, width):
        height = self._doLayout(QRect(0, 0, width, 0), True)
        return height
        
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, False)
        
    def sizeHint(self):
        return self.minimumSize()
        
    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins()
        size += QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size
        
    def _doLayout(self, rect, test_only=False):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self._items:
            style = item.widget().style()
            layout_spacing = style.layoutSpacing(
                QSizePolicy.PushButton,
                QSizePolicy.PushButton,
                Qt.Horizontal
            )
            
            next_x = x + item.sizeHint().width() + layout_spacing
            
            if next_x - layout_spacing > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + spacing
                next_x = x + item.sizeHint().width() + layout_spacing
                line_height = 0
            
            if not test_only:
                item.setGeometry(
                    QRect(QPoint(x, y), item.sizeHint())
                )
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()

class TodoWidget(QWidget):
    def __init__(self, db_manager, user_id):
        super().__init__()
        self.db_manager = db_manager
        self.user_id = user_id
        self.current_project = None
        self.setup_ui()
        self.load_todos()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header section
        header_layout = QHBoxLayout()
        
        # Left side controls
        left_controls = QHBoxLayout()
        left_controls.setSpacing(10)
        
        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Sort", "Priority", "Due Date", "Status"])
        self.sort_combo.setFixedWidth(120)
        left_controls.addWidget(self.sort_combo)
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Tasks", "My Tasks", "Completed", "In Progress", "Pending"])
        self.filter_combo.setFixedWidth(120)
        left_controls.addWidget(self.filter_combo)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search task name")
        self.search_box.setFixedWidth(300)
        left_controls.addWidget(self.search_box)
        
        header_layout.addLayout(left_controls)
        header_layout.addStretch()
        
        # Add Task button
        self.add_task_btn = QPushButton("+ Add Tasks")
        self.add_task_btn.setObjectName("addTaskButton")
        self.add_task_btn.clicked.connect(self.show_add_task_dialog)
        header_layout.addWidget(self.add_task_btn)
        
        main_layout.addLayout(header_layout)

        # Task list
        self.task_list = QTableWidget()
        self.task_list.setColumnCount(6)
        self.task_list.setHorizontalHeaderLabels(["Task Name", "Assigned", "Due Date", "Status", "Priority", "Action"])
        self.task_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.task_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.task_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.task_list.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.task_list.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.task_list.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        
        self.task_list.setColumnWidth(1, 120)  # Assigned
        self.task_list.setColumnWidth(2, 120)  # Due Date
        self.task_list.setColumnWidth(3, 100)  # Status
        self.task_list.setColumnWidth(4, 100)  # Priority
        self.task_list.setColumnWidth(5, 100)  # Action
        
        self.task_list.setShowGrid(False)
        self.task_list.setSelectionMode(QTableWidget.NoSelection)
        self.task_list.verticalHeader().setVisible(False)
        self.task_list.setStyleSheet("""
            QTableWidget {
                background-color: #1e2124;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2c2c2c;
            }
        """)
        
        main_layout.addWidget(self.task_list)

    def load_todos(self):
        todos = self.db_manager.get_todos(self.user_id, self.current_project)
        self.task_list.setRowCount(len(todos))
        
        for row, todo in enumerate(todos):
            # Task name with checkbox
            task_widget = QWidget()
            task_layout = QHBoxLayout(task_widget)
            task_layout.setContentsMargins(0, 0, 0, 0)
            
            checkbox = QCheckBox()
            checkbox.setChecked(todo['status'] == 'COMPLETED')
            task_layout.addWidget(checkbox)
            
            task_name = QLabel(todo['title'])
            task_name.setStyleSheet("color: #ffffff;")
            if todo['status'] == 'COMPLETED':
                task_name.setStyleSheet("color: #9da1a6; text-decoration: line-through;")
            task_layout.addWidget(task_name)
            task_layout.addStretch()
            
            self.task_list.setCellWidget(row, 0, task_widget)
            
            # Assigned
            assigned_widget = QWidget()
            assigned_layout = QHBoxLayout(assigned_widget)
            assigned_layout.setContentsMargins(4, 4, 4, 4)
            assigned_layout.setSpacing(4)
            
            # Add user avatars here
            avatar = QLabel("JD")
            avatar.setStyleSheet("""
                background-color: #404EED;
                color: white;
                border-radius: 12px;
                padding: 4px 8px;
                font-size: 12px;
            """)
            assigned_layout.addWidget(avatar)
            assigned_layout.addStretch()
            
            self.task_list.setCellWidget(row, 1, assigned_widget)
            
            # Due date
            due_date = QLabel(todo['deadline'].strftime("%d %b, %Y"))
            due_date.setStyleSheet("color: #9da1a6;")
            self.task_list.setCellWidget(row, 2, due_date)
            
            # Status
            status_label = QLabel(todo['status'])
            status_label.setAlignment(Qt.AlignCenter)
            status_class = todo['status'].lower().replace(" ", "")
            status_label.setObjectName(f"status{status_class.capitalize()}")
            status_label.setStyleSheet(f"""
                QLabel #{status_label.objectName()} {{
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    font-weight: 500;
                }}
            """)
            self.task_list.setCellWidget(row, 3, status_label)
            
            # Priority
            priority_label = QLabel(todo['priority'])
            priority_label.setAlignment(Qt.AlignCenter)
            priority_class = todo['priority'].lower()
            priority_label.setObjectName(f"priority{priority_class.capitalize()}")
            priority_label.setStyleSheet(f"""
                QLabel #{priority_label.objectName()} {{
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    font-weight: 500;
                }}
            """)
            self.task_list.setCellWidget(row, 4, priority_label)
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 4, 4, 4)
            action_layout.setSpacing(4)
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/trash.png"))
            delete_btn.setObjectName("actionButton")
            delete_btn.clicked.connect(lambda checked, t=todo: self.delete_todo(t))
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setObjectName("actionButton")
            edit_btn.clicked.connect(lambda checked, t=todo: self.edit_todo(t))
            
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(edit_btn)
            action_layout.addStretch()
            
            self.task_list.setCellWidget(row, 5, action_widget)

    def delete_todo(self, todo):
        try:
            reply = QMessageBox.question(
                self,
                "Delete Task",
                "Are you sure you want to delete this task?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.db_manager.delete_todo(todo["id"])
                self.load_todos()
        except Exception as e:
            print(f"Error deleting task: {e}")

    def edit_todo(self, todo):
        try:
            dialog = AddTaskModal(self.db_manager, self, task_data=todo, user_data={"id": 1})
            if dialog.exec_() == QDialog.Accepted:
                self.load_todos()
        except Exception as e:
            print(f"Error editing task: {e}")

    def show_add_task_dialog(self):
        dialog = AddTaskModal(self.db_manager, self, user_data={"id": 1})
        if dialog.exec_() == QDialog.Accepted:
            self.load_todos()

class TaskWidget(QWidget):
    taskDeleted = Signal()
    taskUpdated = Signal()
    taskCompleted = Signal()

    def __init__(self, task_data, db_manager):
        super().__init__()
        self.task_data = task_data
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(15)

        # Drag handle (30px)
        drag_handle = QLabel("⋮⋮")
        drag_handle.setFixedWidth(30)
        drag_handle.setStyleSheet("color: #4a4a4a; font-size: 16px;")
        layout.addWidget(drag_handle)

        # Checkbox (30px)
        self.checkbox = QCheckBox()
        self.checkbox.setFixedWidth(30)
        self.checkbox.setChecked(self.task_data.get("completed", False))
        self.checkbox.stateChanged.connect(self.toggle_completed)
        layout.addWidget(self.checkbox)

        # Task title (flex: 2)
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        if self.task_data.get("completed", False):
            check_icon = QLabel("✓")
            check_icon.setStyleSheet("color: #70c4bc; font-size: 14px;")
            title_layout.addWidget(check_icon)
        
        title = QLabel(self.task_data.get("title", ""))
        title.setWordWrap(True)
        if self.task_data.get("completed", False):
            title.setStyleSheet("color: #9da1a6; text-decoration: line-through;")
        else:
            title.setStyleSheet("color: #ffffff;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        layout.addWidget(title_container, 2)

        # Project (150px)
        project_container = QWidget()
        project_container.setFixedWidth(150)
        project_layout = QHBoxLayout(project_container)
        project_layout.setContentsMargins(0, 0, 0, 0)
        project_layout.setSpacing(2)

        project = QLabel(self.task_data.get("project", ""))
        project.setWordWrap(True)
        project.setStyleSheet("color: #cccccc; font-size: 13px;")
        project_layout.addWidget(project)

        layout.addWidget(project_container)

        # Assigned users (150px)
        assigned_container = QWidget()
        assigned_container.setFixedWidth(150)
        assigned_layout = QHBoxLayout(assigned_container)
        assigned_layout.setContentsMargins(0, 0, 0, 0)
        assigned_layout.setSpacing(2)

        assignees = self.task_data.get("assignees", [])
        for i, user in enumerate(assignees[:3]):
            avatar = QLabel()
            avatar.setFixedSize(24, 24)
            avatar.setStyleSheet(f"""
                background: {['#ff4d4d', '#ffd700', '#70c4bc', '#404EED'][i % 4]};
                border-radius: 12px;
                color: white;
                font-size: 12px;
                font-weight: 500;
            """)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setText(user.get("username", "?")[:1].upper())
            assigned_layout.addWidget(avatar)

        if len(assignees) > 3:
            more_label = QLabel(f"+{len(assignees) - 3}")
            more_label.setFixedSize(24, 24)
            more_label.setStyleSheet("""
                background: #2c2c2c;
                border-radius: 12px;
                color: white;
                font-size: 12px;
            """)
            more_label.setAlignment(Qt.AlignCenter)
            assigned_layout.addWidget(more_label)

        assigned_layout.addStretch()
        layout.addWidget(assigned_container)

        # Due date (120px)
        deadline = self.task_data.get("deadline")
        if deadline:
            try:
                date = QDateTime.fromString(str(deadline), Qt.ISODate)
                if not date.isValid():
                    date = QDateTime.fromString(str(deadline), "yyyy-MM-dd HH:mm:ss")
                
                if date.isValid():
                    due_date = QLabel(date.toString("dd MMM, yyyy"))
                    due_date.setStyleSheet("color: #cccccc; font-size: 13px;")
                else:
                    due_date = QLabel("Invalid date")
                    due_date.setStyleSheet("color: #ff4d4d; font-style: italic; font-size: 13px;")
            except:
                due_date = QLabel("Invalid date")
                due_date.setStyleSheet("color: #ff4d4d; font-style: italic; font-size: 13px;")
        else:
            due_date = QLabel("No deadline")
            due_date.setStyleSheet("color: #9da1a6; font-style: italic; font-size: 13px;")
            
        due_date.setFixedWidth(120)
        layout.addWidget(due_date)

        # Status badge (100px)
        status = self.task_data.get("status", "NEW").upper()
        status_label = QLabel(status)
        status_label.setFixedWidth(100)
        status_label.setAlignment(Qt.AlignCenter)
        
        # Style status badge
        status_styles = {
            "COMPLETED": ("#70c4bc", "white"),  # Turquoise
            "IN-PROGRESS": ("#404EED", "white"),  # Blue
            "PENDING": ("#ffd700", "#333333"),  # Yellow
            "NEW": ("#2c2c2c", "white")  # Dark gray
        }
        
        color, text_color = status_styles.get(status, ("#2c2c2c", "white"))
        status_label.setStyleSheet(f"""
            background: {color};
            color: {text_color};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 500;
        """)
        layout.addWidget(status_label)

        # Priority badge (100px)
        priority = self.task_data.get("priority", "MEDIUM").upper()
        priority_label = QLabel(priority)
        priority_label.setFixedWidth(100)
        priority_label.setAlignment(Qt.AlignCenter)
        
        # Style priority badge
        priority_styles = {
            "CRITICAL": ("#dc3545", "white"),  # Red
            "HIGH": ("#ff4d4d", "white"),  # Light red
            "MEDIUM": ("#ffd700", "#333333"),  # Yellow
            "LOW": ("#70c4bc", "white")  # Turquoise
        }
        
        color, text_color = priority_styles.get(priority, ("#70c4bc", "white"))
        priority_label.setStyleSheet(f"""
            background: {color};
            color: {text_color};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 500;
        """)
        layout.addWidget(priority_label)

        # Action buttons (100px)
        action_container = QWidget()
        action_container.setFixedWidth(100)
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(5)

        delete_btn = QPushButton("🗑️")
        delete_btn.setObjectName("actionButton")
        delete_btn.clicked.connect(self.delete_task)
        action_layout.addWidget(delete_btn)

        edit_btn = QPushButton("✏️")
        edit_btn.setObjectName("actionButton")
        edit_btn.clicked.connect(self.edit_task)
        action_layout.addWidget(edit_btn)

        layout.addWidget(action_container)

        # Set widget styling
        self.setStyleSheet("""
            QWidget {
                background: #1e2124;
            }
            QWidget:hover {
                background: #2c2c2c;
            }
            QLabel {
                background: transparent;
            }
            #actionButton {
                background: transparent;
                border: none;
                color: #808080;
                font-size: 14px;
                padding: 5px;
                border-radius: 4px;
                min-width: 28px;
                min-height: 28px;
            }
            #actionButton:hover {
                background: #363636;
                color: #ffffff;
            }
            QCheckBox {
                background: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #2c2c2c;
                border-radius: 4px;
                background: transparent;
            }
            QCheckBox::indicator:checked {
                background: #404EED;
                border-color: #404EED;
            }
            QCheckBox::indicator:hover {
                border-color: #404EED;
            }
        """)

    def toggle_completed(self, state):
        try:
            self.task_data["completed"] = bool(state)
            self.db_manager.update_todo(
                self.task_data["id"],
                {"completed": bool(state)}
            )
            self.taskCompleted.emit()
        except Exception as e:
            print(f"Error toggling task completion: {e}")

    def edit_task(self):
        try:
            dialog = AddTaskModal(self.db_manager, self, task_data=self.task_data, user_data={"id": 1})
            if dialog.exec_() == QDialog.Accepted:
                self.taskUpdated.emit()
        except Exception as e:
            print(f"Error editing task: {e}")

    def delete_task(self):
        try:
            reply = QMessageBox.question(
                self,
                "Delete Task",
                "Are you sure you want to delete this task?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.db_manager.delete_todo(self.task_data["id"])
                self.taskDeleted.emit()
        except Exception as e:
            print(f"Error deleting task: {e}")
