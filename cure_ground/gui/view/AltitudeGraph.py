import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
import numpy as np

class AltitudeGraph(QFrame):  # Changed to QFrame for better styling
    def __init__(self, status_model, font_family="Arial", parent=None):
        super().__init__(parent)
        self.status_model = status_model
        self.font_family = font_family
        self.is_paused = False
        self.is_minimized = False
        
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #555;
                border-radius: 10px;
            }
        """)
        
        self.setup_ui()
        self.setup_graph()
        self.setup_timer()
        
    def setup_ui(self):
        # Setup the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Altitude Telemetry")
        title_label.setFont(QFont(self.font_family, 12))
        title_label.setStyleSheet("color: white; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Minimize button
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(20, 20)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        self.minimize_btn.clicked.connect(self.toggle_minimize)
        header_layout.addWidget(self.minimize_btn)
        
        # Control buttons
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setFont(QFont(self.font_family, 9))
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b5b84;
                color: white;
                border: 1px solid #1e415e;
                padding: 3px 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a6ea5;
            }
        """)
        self.pause_btn.clicked.connect(self.toggle_pause)
        header_layout.addWidget(self.pause_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setFont(QFont(self.font_family, 9))
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b5b84;
                color: white;
                border: 1px solid #1e415e;
                padding: 3px 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a6ea5;
            }
        """)
        clear_btn.clicked.connect(self.clear_graph)
        header_layout.addWidget(clear_btn)
        
        main_layout.addLayout(header_layout)
        
        # Stats display
        self.stats_frame = QFrame()
        stats_layout = QHBoxLayout(self.stats_frame)
        stats_layout.setContentsMargins(5, 5, 5, 5)
        
        self.stats_labels = {}
        stats_config = [
            ('current', 'Current:'),
            ('max', 'Max:'), 
            ('min', 'Min:'),
            ('average', 'Avg:')
        ]
        
        for stat_id, stat_text in stats_config:
            # Label
            label = QLabel(stat_text)
            label.setFont(QFont(self.font_family, 9))
            label.setStyleSheet("color: #CCCCCC;")
            stats_layout.addWidget(label)
            
            # Value
            value_label = QLabel("N/A")
            value_label.setFont(QFont(self.font_family, 9))
            value_label.setStyleSheet("color: #00FF00; font-weight: bold;")
            stats_layout.addWidget(value_label)
            self.stats_labels[stat_id] = value_label
            
            # Add some spacing between stat pairs
            if stat_id != 'average':
                stats_layout.addSpacing(15)
        
        stats_layout.addStretch()
        main_layout.addWidget(self.stats_frame)
        
        # Graph widget
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('k')  # Black background
        self.graph_widget.setMinimumHeight(300)  # Minimum height
        main_layout.addWidget(self.graph_widget)
        
    def setup_graph(self):
        # Setup the pyqtgraph plot
        # Configure the plot
        self.graph_widget.setLabel('left', 'Altitude', 'm')
        self.graph_widget.setLabel('bottom', 'Time', 's')
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        self.graph_widget.setTitle("", color='w', size='10pt')  # Empty title since we have our own header
        
        # Set plot colors
        self.graph_widget.getAxis('left').setPen('w')
        self.graph_widget.getAxis('bottom').setPen('w')
        
        # Initialize plot curve
        self.curve = self.graph_widget.plot(pen=pg.mkPen(color='#00FF00', width=2))
        
        # Initial plot data
        self.x_data = np.array([])
        self.y_data = np.array([])
        
    def setup_timer(self):
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        self.update_timer.start(100)  # Update every 100ms
        
    def update_plot(self):
        # Update the plot with new data
        if self.is_paused or self.is_minimized:
            return
            
        # Get current data from model
        timestamps, altitudes = self.status_model.get_graph_data()
        
        if timestamps and altitudes:
            # Convert to numpy arrays for better performance
            self.x_data = np.array(timestamps)
            self.y_data = np.array(altitudes)
            
            # Update plot
            self.curve.setData(self.x_data, self.y_data)
            
            # Auto-scale axes
            if len(self.x_data) > 1:
                x_range = self.x_data[-1] - self.x_data[0]
                self.graph_widget.setXRange(max(0, self.x_data[-1] - x_range), self.x_data[-1])
                
                y_min, y_max = min(self.y_data), max(self.y_data)
                y_padding = (y_max - y_min) * 0.1 if y_max != y_min else 50
                self.graph_widget.setYRange(y_min - y_padding, y_max + y_padding)
            
            # Update statistics
            stats = self.status_model.get_graph_stats()
            for stat_id, label in self.stats_labels.items():
                if stat_id in stats:
                    label.setText(f"{stats[stat_id]:.1f}m")
                else:
                    label.setText("N/A")
    
    def toggle_pause(self):
        # Toggle pause state
        self.is_paused = not self.is_paused
        self.pause_btn.setText("Resume" if self.is_paused else "Pause")
        
    def toggle_minimize(self):
        # Toggle minimize state
        self.is_minimized = not self.is_minimized
        self.minimize_btn.setText("+" if self.is_minimized else "−")
        self.stats_frame.setVisible(not self.is_minimized)
        self.graph_widget.setVisible(not self.is_minimized)
        
        # Adjust size when minimized
        if self.is_minimized:
            self.setFixedHeight(40)
        else:
            self.setFixedHeight(400)  # Restore to original height
        
    def clear_graph(self):
        # Clear the graph data
        self.status_model.clear_graph_data()
        self.x_data = np.array([])
        self.y_data = np.array([])
        self.curve.setData(self.x_data, self.y_data)
        
        # Reset stats
        for label in self.stats_labels.values():
            label.setText("N/A")