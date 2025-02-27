import sys, os
import math
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QIcon

def calculate_seconds_shutdown_time(angle) -> int:
    # Get the slider value and map it to seconds
    # example: 45 degree = 15 minutes and modulo 60 to get the remainder seconds
    timer_seconds = ((angle * 60) // 6)
    print(f"angle {angle}  || {timer_seconds} seconds")
    return int(timer_seconds)

def convert_seconds_to_minutes(pure_seconds) -> int:
    hours, remainder = divmod(pure_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    pure_minutes = pure_seconds // 60
    print(f"hours: {hours} || minutes: {minutes} || seconds: {seconds} || pure minutes: {pure_minutes}")
    return int(pure_minutes)

def get_minutes_from_shutdown_time(angle) -> int:
    return convert_seconds_to_minutes(calculate_seconds_shutdown_time(angle))    


class CircularSlider(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Circular Slider")
        self.setGeometry(0, 0, 400, 300)

        # Initialize Slider Variables
        self.value = 0  # Current slider value (0 to 360 degrees)
        self.radius = 80  # Adjusted radius of the circular slider
        self.center = QPoint(int(self.width() * .47), int(self.height() * .31))  # Center of the circle
        self.start_angle = 90  # The angle to start from (top)
        self.total_angle = 0  # Total angle of the circular slider
        root_path = os.getcwd()
        icon_path = os.path.join(root_path, "asset\\icon\\rest.ico")
        print(icon_path)
        self.setWindowIcon(QIcon(icon_path))

    def adaptive_color(self):
        
        def norm_angle_to_255(angle):
            # Ensure angle is in the range 0-360
            angle = angle % 360
            # Linear mapping: 0 -> 0 and 360 -> 255
            return int((angle / 360) * 255)
                
        # Set up the handler circle
        # if self.total_angle > 360:
        # For example, use the modulo of total_angle for a dynamic green component
        # Clamp the extra value to a maximum of 255 for color components
        # adap_extra = self.total_angle - 360
        # green = min(255, int(adap_extra) % 256)
        
        # find normalized value of the total angle of the slider according to the range of 0-360 with 0-255
        adap_extra = norm_angle_to_255(self.total_angle)
        green = min(255, int(adap_extra) % 256)
        adapted_color = QColor(150, green, 255)
        
        return adapted_color
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bg_color = QColor(200, 200, 200)
        handler_color = self.adaptive_color()
        

        # painter.setPen(QPen(QColor(200, 200, 200), 10))  # Light gray background circle
        painter.setPen(QPen(bg_color, 10))  # Light gray background circle
        painter.drawEllipse(int(self.center.x() - self.radius), int(self.center.y() - self.radius),
                            int(2 * self.radius), int(2 * self.radius))
        
        

        # Draw the filled part based on value
        painter.setPen(QPen(handler_color, 10))  # Blue color for the filled part
        painter.drawArc(QRect(int(self.center.x() - self.radius), int(self.center.y() - self.radius),
                              int(2 * self.radius), int(2 * self.radius)),
                         int(self.start_angle * 16), int(-self.value * 16))

        # Draw the handle
        angle = (self.start_angle - self.value) * (math.pi / 180)  # Convert to radians
        x = self.center.x() + self.radius * math.cos(angle)
        y = self.center.y() - self.radius * math.sin(angle)


        # Draw the handle point color
        painter.setBrush(handler_color)
        painter.drawEllipse(QPoint(int(x), int(y)), 8, 8)  # Handle

        # Draw the value inside the circular slider
        painter.setPen(QPen(QColor(150, 150, 255)))  # Black text color
        painter.setFont(QFont("Fira Code", 22))  # Use the default font
        
        time_value = self.get_value()  # Get the current slider value
        
        ### draw value in the center of the circle
        painter.setFont(QFont("Fira Code", 30))  # Use the default font
        painter.setPen(QPen(self.adaptive_color()))  # Black text color
        rect = QRect(self.center.x() - 50, self.center.y() - 35, 100, 40)  # Define a rectangle for the text
        painter.drawText(rect, Qt.AlignCenter, f"{get_minutes_from_shutdown_time(time_value)}")  # Draw the value
        
        painter.setPen(QPen(QColor(150, 150, 255)))  # Black text color
        painter.setFont(QFont("Fira Code", 14))  # Use the default font
        painter.drawText(self.center.x() - 35, self.center.y() + 30, f"Minutes")  # Draw the value
        

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
        
        # detect direction of the rotation
        diff = adjusted_angle - (self.total_angle % 360)
        
        handle_crossing_right = abs(angle) < 90
        handle_crossing_left = not handle_crossing_right
        
        
        # Handle boundary crossing (e.g., 350° → 10° should be +20, not -340)
        if diff > 180:
            diff -= 360
        if diff < -180:
            diff += 360
        
        # add the difference to the total angle    
        self.total_angle += diff
        
        # assign final total value and prevent the total angle from going below 0 (negative)
        self.total_angle = max(0, self.total_angle)
            
        # Ensure total_angle is within the correct range
        self.value = adjusted_angle
        
        
        # print(f"adjusted angle: {int(adjusted_angle)} || total angle: {int(self.total_angle)} || angle: {int(angle)}")
        
        self.update()  # Redraw the widget

    def get_value(self):
        self.total_angle = int(self.total_angle)
        return self.total_angle  # Return the current slider value

    def reset_value(self):
        self.value = 0
        self.total_angle = 0
        self.update()



class TimerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Shutdown Timer")
        self.screen = QApplication.primaryScreen()
        self.width, self.height = 400, 500
        # set initial window size to middle of the screen x, y
        self.x = (self.screen.size().width() - self.width) // 2
        self.y = (self.screen.size().height() - self.height) * .4
        self.setGeometry(int(self.x), int(self.y), int(self.width), int(self.height))
        self.setFixedSize(self.width, self.height)
        root_path = os.getcwd()
        icon_path = os.path.join(root_path, "asset\\icon\\rest.ico")
        print(icon_path)
        self.setWindowIcon(QIcon(icon_path))
    

        # Create UI Elements
        self.layout = QVBoxLayout()
        self.layout.addSpacing(15)
        
        # Create Circular Slider
        self.circular_slider = CircularSlider()
        self.layout.addWidget(self.circular_slider)
        # Add a spacer between the slider and the buttons
        # self.layout.addSpacing(20)

        # Timer Input Fields (optional if you want direct input)
        self.time_input = QLineEdit(self)
        self.time_input.setPlaceholderText("Enter time in [minutes] or use slider")
        self.layout.addWidget(self.time_input)
        # Add a spacer to create some space between the input and the circular slider
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
            print(f"Slider Value: {slider_value}")
            # example: 45 degree = 15 minutes and modulo 60 to get the remainder seconds
            self.timer_seconds = ((slider_value * 60) // 6)
            self.timer_mod = self.timer_seconds % 100
            self.timer_seconds = self.timer_seconds - self.timer_mod
            
            self.timer_seconds = [10, self.timer_seconds][self.timer_seconds > 0]

            # Disable user input and adjust the start button state
            self.time_input.setDisabled(True)
            self.circular_slider.setDisabled(True)
            self.start_button.setText("Timer Running...")
            self.is_running = True


            # disable start button when timer is running
            self.start_button.setDisabled(True)
            
            shutdown_command = f"shutdown -s -t {int(self.timer_seconds)}"
            print("execute cmd: " + shutdown_command)
            os.system(shutdown_command)
            
        else:
            pass


    def update_timer(self):
        # real-time countdown
        if self.timer_seconds > 0 and self.is_running:
            self.timer_seconds -= 1
            hours, remainder = divmod(self.timer_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_display.setText(f"Time Left: {hours:02}h:{minutes:02}m:{seconds:02}s")
        
        # when timer is up
        else:
            self.countdown_timer.stop()
            self.timer_display.setText("Time's up!")
            self.start_button.setText("Start Timer")
            self.reset_timer()


    def reset_timer(self):
        self.is_running = False
        os.system("shutdown -a")
        self.time_input.setEnabled(True)
        self.circular_slider.setEnabled(True)
        self.time_input.clear()
        self.timer_display.setText("Time Left: 00:00:00")
        self.start_button.setText("Start Timer")
        self.circular_slider.reset_value()
        
        # enable start button when timer is reset
        self.start_button.setDisabled(False)
        
        
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimerApp()
    sys.exit(app.exec_())
