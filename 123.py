from PyQt6.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt6.QtCore import QTimer
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.counter = 0

        # Create label to display seconds
        self.label = QLabel("0", self)
        self.label.setGeometry(50, 50, 100, 30)

        # Create and setup timer
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1000ms = 1 second [[6]]
        self.timer.timeout.connect(self.update_counter)
        self.timer.start()

        self.setGeometry(100, 100, 200, 150)
        self.setWindowTitle("Seconds Counter")

    def update_counter(self):
        self.counter += 1
        self.label.setText(str(self.counter))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())