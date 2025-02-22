import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import QEvent, Qt


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
        self.setFixedSize(300, 150)

        # Текстовое поле внутри фигуры
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setGeometry(10, 10, 280, 130)  # Учет отступов
        self.hide()

    def update_text(self, text):
        """Обновляет текст внутри фигуры."""
        self.label.setText(text)


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 800, 600
        self.setMinimumSize(self.window_width, self.window_height)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.button = QPushButton('Start')
        self.my_label = QLabel('MyText')
        self.layout.addWidget(self.my_label)
        self.layout.addWidget(self.button)


        # Устанавливаем фильтр событий на кнопку
        self.button.installEventFilter(self)

        # Создаем окно-форму для текста
        self.shape_window = ShapeWindow(self)
        self.connects()

    def click_start(self):
        print(12345)
        self.my_label.setText("xxxxxx xxxxx")

    def eventFilter(self, source, event):
        if source == self.button:
            if event.type() == QEvent.Type.Enter:
                self.show_shape_window("Это текст внутри фигуры!")
            elif event.type() == QEvent.Type.Leave:
                self.shape_window.hide()
        return super().eventFilter(source, event)

    def show_shape_window(self, text):
        """Показывает фигуру с текстом справа от главного окна."""
        self.shape_window.update_text(text)

        # Расчет позиции для окна-формы
        x = self.geometry().x() + self.width()  # Правый край главного окна
        y = self.geometry().y() + self.button.y()

        self.shape_window.move(x, y)
        self.shape_window.show()
        print(3456)
        print(55555)
        print(55545555587855)

    def connects(self):
        self.button.clicked.connect(self.click_start)



if __name__ == '__main__':
    app = QApplication(sys.argv)

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')
