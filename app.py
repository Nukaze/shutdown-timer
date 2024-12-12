import sys
import math
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QIcon


class CircularSlider(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Circular Slider")
        self.setGeometry(100, 100, 300, 300)

        # Initialize Slider Variables
        self.value = 0  # Current slider value (0 to 360 degrees)
        self.radius = 80  # Adjusted radius of the circular slider
        self.center = QPoint(self.width() // 2, self.height() // 2)  # Center of the circle
        self.start_angle = 90  # The angle to start from (top)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set up the background circle
        painter.setPen(QPen(QColor(200, 200, 200), 10))  # Light gray background circle
        painter.drawEllipse(int(self.center.x() - self.radius), int(self.center.y() - self.radius),
                            int(2 * self.radius), int(2 * self.radius))

        # Draw the filled part based on value
        painter.setPen(QPen(QColor(50, 150, 255), 10))  # Blue color for the filled part
        painter.drawArc(QRect(int(self.center.x() - self.radius), int(self.center.y() - self.radius),
                              int(2 * self.radius), int(2 * self.radius)),
                         int(self.start_angle * 16), int(-self.value * 16))

        # Draw the handle
        angle = (self.start_angle - self.value) * (math.pi / 180)  # Convert to radians
        x = self.center.x() + self.radius * math.cos(angle)
        y = self.center.y() - self.radius * math.sin(angle)
        painter.setBrush(QColor(255, 0, 0))  # Red handle
        painter.drawEllipse(QPoint(int(x), int(y)), 10, 10)  # Handle

        # Draw the value inside the circular slider
        painter.setPen(QPen(QColor(0, 0, 0)))  # Black text color
        painter.setFont(self.font())  # Use the default font
        painter.drawText(self.center.x() - 20, self.center.y() + 10, f"{int(self.value)}°")  # Draw the value

    def mousePressEvent(self, event):
        if self.is_inside_circle(event.pos()):
            self.update_angle(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.update_angle(event.pos())

    def is_inside_circle(self, point):
        distance = math.sqrt((point.x() - self.center.x())**2 + (point.y() - self.center.y())**2)
        return distance <= self.radius

    def update_angle(self, point):
        # Calculate the angle of the mouse pointer
        dx = point.x() - self.center.x()
        dy = point.y() - self.center.y()
        angle = math.degrees(math.atan2(dy, dx))

        # Calculate the slider value (0-360) with smoother step by adjusting precision
        adjusted_angle = (angle + 90) % 360  # Adjusting angle to match top as starting point
        self.value = adjusted_angle
        self.update()  # Redraw the widget

    def get_value(self):
        return self.value  # Return the current slider value





class TimerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Shutdown Timer")
        self.screen = QApplication.primaryScreen()
        self.width, self.height = 500, 800
        # set initial window size to middle of the screen x, y
        self.x = (self.screen.size().width() - self.width) // 2
        self.y = (self.screen.size().height() - self.height) * .4
        self.setGeometry(self.x, self.y, self.width, self.height)
        
        self.setFixedSize(self.width, self.height)
        self.setWindowIcon(QIcon("asset/icon/sleep_score.svg"))
    

        # Create UI Elements
        self.layout = QVBoxLayout()

        # Timer Input Fields (optional if you want direct input)
        self.label = QLabel("Set Timer (hh:mm:ss):", self)
        self.layout.addWidget(self.label)

        self.time_input = QLineEdit(self)
        self.time_input.setPlaceholderText("Enter time (hh:mm:ss) or use slider")
        self.layout.addWidget(self.time_input)

        # Add a spacer to create some space between the input and the circular slider
        self.layout.addSpacing(20)

        # Create Circular Slider
        self.circular_slider = CircularSlider()
        self.layout.addWidget(self.circular_slider)

        # Add a spacer between the slider and the buttons
        self.layout.addSpacing(20)

        # Start and Reset buttons
        self.start_button = QPushButton("Start Timer", self)
        self.start_button.clicked.connect(self.start_timer)
        self.layout.addWidget(self.start_button)

        self.reset_button = QPushButton("Reset Timer", self)
        self.reset_button.clicked.connect(self.reset_timer)
        self.layout.addWidget(self.reset_button)

        # Countdown Display
        self.timer_display = QLabel("Time Left: 00:00:00", self)
        self.layout.addWidget(self.timer_display)

        # Set up a timer for countdown
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_timer)

        # Set the layout and show the window
        self.setLayout(self.layout)
        self.show()

        # Timer variables
        self.timer_seconds = 0
        self.is_running = False

    def start_timer(self):
        if not self.is_running:
            # Get the slider value and map it to seconds
            slider_value = self.circular_slider.get_value()
            self.timer_seconds = slider_value * 10  # Example: 1 degree = 10 seconds

            # Disable user input and adjust the start button state
            self.time_input.setDisabled(True)
            self.circular_slider.setDisabled(True)
            self.start_button.setText("Timer Running...")
            self.is_running = True

            # Start the countdown
            self.countdown_timer.start(1000)  # 1 second intervals
        else:
            pass

    def update_timer(self):
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            hours, remainder = divmod(self.timer_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_display.setText(f"Time Left: {hours:02}:{minutes:02}:{seconds:02}")
        else:
            self.countdown_timer.stop()
            self.timer_display.setText("Time's up!")
            self.start_button.setText("Start Timer")
            self.reset_timer()

    def reset_timer(self):
        self.is_running = False
        self.time_input.setEnabled(True)
        self.circular_slider.setEnabled(True)
        self.time_input.clear()
        self.timer_display.setText("Time Left: 00:00:00")
        self.start_button.setText("Start Timer")
        
        
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimerApp()
    sys.exit(app.exec_())
