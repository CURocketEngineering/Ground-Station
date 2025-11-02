import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import numpy as np
import time

class AltitudeGraph(QFrame):
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
        
        # Ensure this widget stays on top
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop, True)
        
        self.setup_ui()
        self.setup_graph()
        self.setup_timer()
        
    def setup_ui(self):
        """Setup the main layout"""
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
        
        # Update frequency indicator
        self.update_freq_label = QLabel("0 Hz")
        self.update_freq_label.setFont(QFont(self.font_family, 9))
        self.update_freq_label.setStyleSheet("color: #CCCCCC;")
        header_layout.addWidget(self.update_freq_label)
        
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
        self.graph_widget.setBackground('k')
        self.graph_widget.setMinimumHeight(450)
        main_layout.addWidget(self.graph_widget)
        
    def setup_graph(self):
        """Setup the pyqtgraph plot"""
        # Configure the plot for better performance
        self.graph_widget.setLabel('left', 'Altitude (m)')
        self.graph_widget.setLabel('bottom', 'Time (s)')
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Disable auto SI prefix scaling on axes (prevents k, M prefixes)
        self.graph_widget.getAxis('left').enableAutoSIPrefix(False)
        self.graph_widget.getAxis('bottom').enableAutoSIPrefix(False)
        
        # Set plot colors
        self.graph_widget.getAxis('left').setPen('w')
        self.graph_widget.getAxis('bottom').setPen('w')
        
        # Initialize plot curve with anti-aliasing disabled for performance
        self.curve = self.graph_widget.plot(pen=pg.mkPen(color='#00FF00', width=2), antialias=False)
        
        # Initial plot data
        self.x_data = np.array([])
        self.y_data = np.array([])
        
        # Performance tracking
        self.update_count = 0
        self.last_update_time = time.time()
        self.last_data_length = 0
        
    def setup_timer(self):
        """Setup update timer - FAST real-time updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        self.update_timer.start(16)  # ~60 FPS for smooth real-time feel
        
    def update_plot(self):
        """Update the plot with new data"""
        if self.is_paused or self.is_minimized:
            return
            
        # Get current data from model
        timestamps, altitudes = self.status_model.get_graph_data()
        
        if timestamps and altitudes:
            # Convert to numpy arrays for better performance
            self.x_data = np.array(timestamps)
            self.y_data = np.array(altitudes)
            
            # Only update plot if we have new data
            current_length = len(self.x_data)
            if current_length != self.last_data_length:
                # Update plot
                self.curve.setData(self.x_data, self.y_data)
                self.last_data_length = current_length
                
                # Auto-scale axes for real-time feel
                if len(self.x_data) > 1:
                    # For short flights (< 60s), show all data
                    # For longer flights, show scrolling 60s window
                    total_duration = self.x_data[-1] - self.x_data[0]
                    
                    if total_duration <= 60.0:
                        # Show all data for short flights
                        x_min = self.x_data[0]
                        x_max = self.x_data[-1]
                    else:
                        # Scrolling window for longer flights
                        window_size = 60.0  # seconds
                        x_max = self.x_data[-1]
                        x_min = max(self.x_data[0], x_max - window_size)
                    
                    # Set X range
                    self.graph_widget.setXRange(x_min, x_max, padding=0.02)
                    
                    # Set Y range based on visible data
                    visible_indices = (self.x_data >= x_min) & (self.x_data <= x_max)
                    if np.any(visible_indices):
                        visible_y = self.y_data[visible_indices]
                        y_min, y_max = np.min(visible_y), np.max(visible_y)
                        y_padding = (y_max - y_min) * 0.15 if y_max != y_min else 50
                        self.graph_widget.setYRange(y_min - y_padding, y_max + y_padding, padding=0)
            
            # Update statistics
            stats = self.status_model.get_graph_stats()
            for stat_id, label in self.stats_labels.items():
                if stat_id in stats:
                    label.setText(f"{stats[stat_id]:.1f}m")
                else:
                    label.setText("N/A")
            
            # Update frequency display
            self.update_count += 1
            current_time = time.time()
            if current_time - self.last_update_time >= 1.0:
                freq = self.update_count / (current_time - self.last_update_time)
                self.update_freq_label.setText(f"{freq:.1f} Hz")
                self.update_count = 0
                self.last_update_time = current_time
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.is_paused = not self.is_paused
        self.pause_btn.setText("Resume" if self.is_paused else "Pause")
        
    def toggle_minimize(self):
        """Toggle minimize state"""
        self.is_minimized = not self.is_minimized
        self.minimize_btn.setText("+" if self.is_minimized else "−")
        self.stats_frame.setVisible(not self.is_minimized)
        self.graph_widget.setVisible(not self.is_minimized)
        
        # Adjust size when minimized
        if self.is_minimized:
            self.setFixedHeight(40)
        else:
            self.setFixedHeight(550)
        
    def clear_graph(self):
        """Clear the graph data"""
        self.status_model.clear_graph_data()
        self.x_data = np.array([])
        self.y_data = np.array([])
        self.curve.setData(self.x_data, self.y_data)
        self.last_data_length = 0
        
        # Reset stats
        for label in self.stats_labels.values():
            label.setText("N/A")