from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QScrollArea, QFrame, QPushButton, QGridLayout,
                               QProgressBar, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QDate, QDateTime, QTime
from PySide6.QtGui import QColor, QFont
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
import os
from PySide6.QtGui import QPainter

class DashboardWidget(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.load_stylesheet()
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(30000)  # Update every 30 seconds
    
    def load_stylesheet(self):
        style_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'style.qss')
        with open(style_path, 'r') as f:
            self.setStyleSheet(f.read())
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(20)
        
        # Welcome section
        welcome_frame = QFrame()
        welcome_layout = QVBoxLayout(welcome_frame)
        
        welcome_label = QLabel(f"Welcome back, {self.user_data['username']}!")
        welcome_label.setProperty("heading", True)
        welcome_layout.addWidget(welcome_label)
        
        container_layout.addWidget(welcome_frame)
        
        # Stats section
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)
        
        # Add stats widgets
        self.add_stat_widget(stats_layout, "Tasks Due Today", "5", 0, 0)
        self.add_stat_widget(stats_layout, "Messages", "3", 0, 1)
        self.add_stat_widget(stats_layout, "Hours Tracked", "6.5", 0, 2)
        self.add_stat_widget(stats_layout, "Files", "12", 0, 3)
        
        container_layout.addWidget(stats_frame)
        
        # Charts section
        charts_frame = QFrame()
        charts_layout = QHBoxLayout(charts_frame)
        
        # Time distribution chart
        time_chart = self.create_time_chart()
        charts_layout.addWidget(time_chart)
        
        # Task status chart
        task_chart = self.create_task_chart()
        charts_layout.addWidget(task_chart)
        
        container_layout.addWidget(charts_frame)
        
        # Set scroll widget
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    def add_stat_widget(self, layout, title, value, row, col):
        frame = QFrame()
        stat_layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setProperty("subtext", True)
        stat_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setProperty("heading", True)
        stat_layout.addWidget(value_label)
        
        layout.addWidget(frame, row, col)
    
    def create_time_chart(self):
        # Create chart
        chart = QChart()
        chart.setBackgroundBrush(QColor("#2c2c2c"))
        chart.setTitleBrush(QColor("#cccccc"))
        chart.setTitle("Time Distribution")
        
        # Create series
        series = QPieSeries()
        series.append("Development", 4)
        series.append("Meetings", 2)
        series.append("Planning", 1.5)
        
        # Set slice colors
        series.slices()[0].setBrush(QColor("#3498db"))
        series.slices()[1].setBrush(QColor("#2ecc71"))
        series.slices()[2].setBrush(QColor("#e74c3c"))
        
        chart.addSeries(series)
        
        # Create chart view
        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)
        
        return chartView
    
    def create_task_chart(self):
        # Create chart
        chart = QChart()
        chart.setBackgroundBrush(QColor("#2c2c2c"))
        chart.setTitleBrush(QColor("#cccccc"))
        chart.setTitle("Task Status")
        
        # Create series
        set0 = QBarSet("Tasks")
        set0.append([4, 8, 6])
        set0.setColor(QColor("#3498db"))
        
        series = QBarSeries()
        series.append(set0)
        
        chart.addSeries(series)
        
        # Create axes
        categories = QBarCategoryAxis()
        categories.append(["To Do", "In Progress", "Done"])
        categories.setLabelsColor(QColor("#cccccc"))
        
        axisY = QValueAxis()
        axisY.setRange(0, 10)
        axisY.setLabelsColor(QColor("#cccccc"))
        
        chart.setAxisX(categories, series)
        chart.setAxisY(axisY, series)
        
        # Create chart view
        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)
        
        return chartView
    
    def update_dashboard(self):
        # Update dashboard data here
        pass
