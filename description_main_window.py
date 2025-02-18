from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtGui import QPainter, QBrush, QPen,QColor
from PyQt6.QtCore import Qt, QRectF
import sys

class ShapeWindow(QWidget):
    """Окно в форме закругленного прямоугольника с текстом."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setFixedSize(320, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Делаем фон прозрачным

        # Текстовое поле внутри фигуры
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setGeometry(20, 20, 280, 260)  # Отступы внутри формы
        self.hide()

    def paintEvent(self, event):
        """Рисует закругленный прямоугольник с заливкой внутри."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Сглаживание

        # Размер и радиус закругления
        rect = QRectF(0, 0, self.width(), self.height())
        radius = 20

        # Устанавливаем заливку только внутри фигуры
        brush = QBrush(QColor("honeydew"))  # Цвет фона
        painter.setBrush(brush)

        # Граница
        pen = QPen(Qt.GlobalColor.black, 2)  # Цвет и толщина границы
        painter.setPen(pen)

        # Рисуем саму фигуру
        painter.drawRoundedRect(rect, radius, radius)

    def update_text(self, text):
        """Обновляет текст внутри фигуры."""
        self.label.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShapeWindow()
    window.show()
    sys.exit(app.exec())
