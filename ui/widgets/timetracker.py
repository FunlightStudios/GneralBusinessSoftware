from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFrame, QScrollArea,
                               QCalendarWidget, QTableWidget, QTableWidgetItem,
                               QHeaderView)
from PySide6.QtCore import Qt, QTimer, QTime, QDate, QDateTime
from PySide6.QtGui import QColor

class TimeTrackerWidget(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.is_checked_in = False
        self.current_session_start = None
        self.setup_ui()
        
        # Setup clock timer
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Time Tracking")
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
        content_layout = QVBoxLayout()
        
        # Clock section
        clock_frame = QFrame()
        clock_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 3px;
                padding: 10px;
            }
        """)
        clock_layout = QHBoxLayout()
        
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #3498db;
            }
        """)
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #95a5a6;
            }
        """)
        
        # Update both labels
        self.update_clock()
        
        clock_layout.addWidget(self.clock_label, alignment=Qt.AlignCenter)
        clock_layout.addWidget(self.date_label, alignment=Qt.AlignCenter)
        clock_frame.setLayout(clock_layout)
        content_layout.addWidget(clock_frame)
        
        # Check in/out section
        checkin_frame = QFrame()
        checkin_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 3px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        checkin_layout = QVBoxLayout()
        
        # Status and timer
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Currently: Checked Out")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #e74c3c;
            }
        """)
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #3498db;
            }
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.timer_label)
        checkin_layout.addLayout(status_layout)
        
        # Check in/out button
        self.checkin_button = QPushButton("Check In")
        self.checkin_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 3px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        self.checkin_button.clicked.connect(self.toggle_checkin)
        checkin_layout.addWidget(self.checkin_button)
        
        checkin_frame.setLayout(checkin_layout)
        content_layout.addWidget(checkin_frame)
        
        # Time records table
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 3px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        table_layout = QVBoxLayout()
        
        table_header = QLabel("Recent Time Records")
        table_header.setStyleSheet("font-size: 16px;")
        table_layout.addWidget(table_header)
        
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(4)
        self.records_table.setHorizontalHeaderLabels(["Date", "Check In", "Check Out", "Duration"])
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.records_table.setStyleSheet("""
            QTableWidget {
                background-color: #34495e;
                border: none;
            }
            QTableWidget::item {
                color: #ecf0f1;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: #3498db;
                padding: 5px;
                border: none;
            }
        """)
        table_layout.addWidget(self.records_table)
        
        table_frame.setLayout(table_layout)
        content_layout.addWidget(table_frame)
        
        content_frame.setLayout(content_layout)
        layout.addWidget(content_frame)
        
        self.setLayout(layout)
        self.update_records()
        
        # Setup session timer
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_session_time)
    
    def update_clock(self):
        current_time = QTime.currentTime()
        if hasattr(self, 'clock_label'):
            self.clock_label.setText(current_time.toString("hh:mm:ss"))
            self.update_date()
    
    def update_date(self):
        if hasattr(self, 'date_label'):
            current_date = QDate.currentDate()
            self.date_label.setText(current_date.toString("dddd, MMMM d, yyyy"))
    
    def toggle_checkin(self):
        if not self.is_checked_in:
            # Check in
            self.is_checked_in = True
            self.current_session_start = QDateTime.currentDateTime()
            self.checkin_button.setText("Check Out")
            self.checkin_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 3px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            self.status_label.setText("Currently: Checked In")
            self.status_label.setStyleSheet("QLabel { font-size: 18px; color: #27ae60; }")
            self.session_timer.start(1000)
        else:
            # Check out
            self.is_checked_in = False
            end_time = QDateTime.currentDateTime()
            self.checkin_button.setText("Check In")
            self.checkin_button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 3px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #219a52;
                }
            """)
            self.status_label.setText("Currently: Checked Out")
            self.status_label.setStyleSheet("QLabel { font-size: 18px; color: #e74c3c; }")
            self.session_timer.stop()
            self.timer_label.setText("00:00:00")
            
            # Save the time record
            self.db_manager.create_time_record(
                user_id=self.user_data['id'],
                check_in=self.current_session_start.toString(Qt.ISODate),
                check_out=end_time.toString(Qt.ISODate)
            )
            self.current_session_start = None
            self.update_records()
    
    def update_session_time(self):
        if self.current_session_start:
            current_duration = self.current_session_start.secsTo(QDateTime.currentDateTime())
            hours = current_duration // 3600
            minutes = (current_duration % 3600) // 60
            seconds = current_duration % 60
            self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def update_records(self):
        records = self.db_manager.get_time_records(self.user_data['id'])
        self.records_table.setRowCount(len(records))
        
        for i, record in enumerate(records):
            check_in = QDateTime.fromString(record['check_in'], Qt.ISODate)
            check_out = QDateTime.fromString(record['check_out'], Qt.ISODate)
            duration_secs = check_in.secsTo(check_out)
            hours = duration_secs // 3600
            minutes = (duration_secs % 3600) // 60
            
            date_item = QTableWidgetItem(check_in.toString("yyyy-MM-dd"))
            check_in_item = QTableWidgetItem(check_in.toString("hh:mm:ss"))
            check_out_item = QTableWidgetItem(check_out.toString("hh:mm:ss"))
            duration_item = QTableWidgetItem(f"{hours:02d}:{minutes:02d}")
            
            self.records_table.setItem(i, 0, date_item)
            self.records_table.setItem(i, 1, check_in_item)
            self.records_table.setItem(i, 2, check_out_item)
            self.records_table.setItem(i, 3, duration_item)
