from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFrame, QCalendarWidget,
                               QScrollArea, QLineEdit, QTextEdit, QComboBox,
                               QMessageBox)
from PySide6.QtCore import Qt, QDate, QDateTime, QTimer
from PySide6.QtGui import QColor, QTextCharFormat

class CalendarWidget(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.setup_ui()
        
        # Setup refresh timer for events
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_calendar_events)
        self.refresh_timer.start(60000)  # Refresh every minute
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Calendar")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #ffffff;
                padding: 10px;
                background-color: #2c3e50;
                border-radius: 5px;
            }
        """)
        layout.addWidget(header)
        
        # Main content
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.StyledPanel)
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel {
                color: #ecf0f1;
            }
        """)
        content_layout = QHBoxLayout()
        
        # Left side - Calendar
        calendar_frame = QFrame()
        calendar_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 3px;
                padding: 10px;
            }
        """)
        calendar_layout = QVBoxLayout()
        
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #34495e;
            }
            QCalendarWidget QWidget {
                alternate-background-color: #2c3e50;
            }
            QCalendarWidget QTableView {
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QMenu {
                background-color: #2c3e50;
                color: white;
            }
            QCalendarWidget QSpinBox {
                background-color: #2c3e50;
                color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #7f8c8d;
            }
        """)
        self.calendar.clicked.connect(self.date_selected)
        calendar_layout.addWidget(self.calendar)
        
        calendar_frame.setLayout(calendar_layout)
        content_layout.addWidget(calendar_frame)
        
        # Right side - Events
        events_frame = QFrame()
        events_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 3px;
                padding: 10px;
                margin-left: 10px;
            }
        """)
        events_layout = QVBoxLayout()
        
        # Add event section
        add_event_label = QLabel("Add Event")
        add_event_label.setStyleSheet("font-size: 16px;")
        events_layout.addWidget(add_event_label)
        
        # Event title
        title_layout = QHBoxLayout()
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        self.title_input.setStyleSheet("""
            QLineEdit {
                background-color: #34495e;
                border: 1px solid #3498db;
                border-radius: 3px;
                padding: 5px;
                color: white;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        events_layout.addLayout(title_layout)
        
        # Event description
        desc_label = QLabel("Description:")
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        self.desc_input.setStyleSheet("""
            QTextEdit {
                background-color: #34495e;
                border: 1px solid #3498db;
                border-radius: 3px;
                padding: 5px;
                color: white;
            }
        """)
        events_layout.addWidget(desc_label)
        events_layout.addWidget(self.desc_input)
        
        # Event type
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Meeting", "Deadline", "Reminder", "Other"])
        self.type_combo.setStyleSheet("""
            QComboBox {
                background-color: #34495e;
                border: 1px solid #3498db;
                border-radius: 3px;
                padding: 5px;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-width: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #34495e;
                color: white;
                selection-background-color: #3498db;
            }
        """)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        events_layout.addLayout(type_layout)
        
        # Add event button
        add_button = QPushButton("Add Event")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        add_button.clicked.connect(self.add_event)
        events_layout.addWidget(add_button)
        
        # Events list
        events_label = QLabel("Events for Selected Date")
        events_label.setStyleSheet("font-size: 16px; margin-top: 10px;")
        events_layout.addWidget(events_label)
        
        self.events_scroll = QScrollArea()
        self.events_scroll.setWidgetResizable(True)
        self.events_content = QWidget()
        self.events_list_layout = QVBoxLayout(self.events_content)
        self.events_scroll.setWidget(self.events_content)
        self.events_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget {
                background-color: transparent;
            }
        """)
        events_layout.addWidget(self.events_scroll)
        
        events_frame.setLayout(events_layout)
        content_layout.addWidget(events_frame)
        
        content_frame.setLayout(content_layout)
        layout.addWidget(content_frame)
        
        self.setLayout(layout)
        self.update_calendar_events()
    
    def get_event_color(self, event_type):
        colors = {
            "Meeting": QColor("#3498db"),    # Blue
            "Deadline": QColor("#e74c3c"),   # Red
            "Reminder": QColor("#f1c40f"),   # Yellow
            "Other": QColor("#95a5a6")       # Gray
        }
        return colors.get(event_type, QColor("#95a5a6"))
    
    def update_calendar_events(self):
        # Clear all date formats
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Get all events
        events = self.db_manager.get_calendar_events(self.user_data['id'])
        
        # Mark dates with events
        for event in events:
            date = QDate.fromString(event['date'], Qt.ISODate)
            fmt = QTextCharFormat()
            fmt.setBackground(self.get_event_color(event['type']))
            self.calendar.setDateTextFormat(date, fmt)
        
        # Update events list for selected date
        self.update_events_list()
    
    def date_selected(self):
        self.update_events_list()
    
    def update_events_list(self):
        # Clear existing events
        while self.events_list_layout.count():
            child = self.events_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        selected_date = self.calendar.selectedDate().toString(Qt.ISODate)
        events = self.db_manager.get_calendar_events(self.user_data['id'], selected_date)
        
        for event in events:
            event_frame = QFrame()
            event_frame.setFrameStyle(QFrame.StyledPanel)
            event_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.get_event_color(event['type']).name()};
                    border-radius: 5px;
                    padding: 10px;
                    margin: 2px;
                }}
                QLabel {{
                    color: white;
                }}
            """)
            
            event_layout = QVBoxLayout()
            
            # Header with title and type
            header_layout = QHBoxLayout()
            title = QLabel(f"<b>{event['title']}</b>")
            type_label = QLabel(f"({event['type']})")
            header_layout.addWidget(title)
            header_layout.addWidget(type_label)
            header_layout.addStretch()
            
            # Delete button
            delete_btn = QPushButton("×")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.2);
                    color: white;
                    border: none;
                    padding: 2px 6px;
                    border-radius: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.4);
                }
            """)
            delete_btn.clicked.connect(lambda checked, e=event: self.delete_event(e))
            header_layout.addWidget(delete_btn)
            
            event_layout.addLayout(header_layout)
            
            # Description
            if event['description']:
                desc = QLabel(event['description'])
                desc.setWordWrap(True)
                event_layout.addWidget(desc)
            
            event_frame.setLayout(event_layout)
            self.events_list_layout.addWidget(event_frame)
        
        # Add stretch at the end
        self.events_list_layout.addStretch()
    
    def add_event(self):
        title = self.title_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        event_type = self.type_combo.currentText()
        date = self.calendar.selectedDate().toString(Qt.ISODate)
        
        if not title:
            QMessageBox.warning(self, "Error", "Please enter an event title")
            return
        
        self.db_manager.create_calendar_event(
            user_id=self.user_data['id'],
            title=title,
            description=description,
            type=event_type,
            date=date
        )
        
        # Clear inputs
        self.title_input.clear()
        self.desc_input.clear()
        self.type_combo.setCurrentIndex(0)
        
        # Update calendar and events list
        self.update_calendar_events()
    
    def delete_event(self, event):
        reply = QMessageBox.question(
            self,
            "Delete Event",
            f"Delete event '{event['title']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db_manager.delete_calendar_event(event['id'])
            self.update_calendar_events()
