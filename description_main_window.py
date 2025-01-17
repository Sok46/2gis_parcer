# import sys
# from PyQt6.QtWidgets import QApplication,  QPushButton, QVBoxLayout
# from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt


class ShapeWindow(QWidget):
    """Окно в форме фигуры для текста."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setStyleSheet("""
            background-color: lightblue;
            border: 2px solid black;
            border-radius: 20px;
        """)
        self.setFixedSize(300, 250)

        # Текстовое поле внутри фигуры
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setGeometry(10, 10, 280, 230)  # Учет отступов
        self.hide()

    def update_text(self, text):
        """Обновляет текст внутри фигуры."""
        self.label.setText(text)