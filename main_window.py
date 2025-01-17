import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,QHBoxLayout)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt,QEvent
from multy_query import WindowMultyQuery
from Urban_parser import WindowAuth
from description_main_window import ShapeWindow

class MainWindow(QWidget):
    def __init__(self, count_queries=0, id_person=10):
        super().__init__()
        self.count_queries = count_queries
        self.id_person = id_person

        self.shape_window = ShapeWindow(self)

        # Сопоставление кнопок и описаний
        self.descriptions = {}

        self.initializeUI()

    def initializeUI(self):
        """Set up the application's GUI."""
        self.setWindowTitle("Urban parser")
        self.setUpMainWindow()
        self.show()
    # Функции при наведении на кнопку
    def eventFilter(self, source, event):
        if source in self.descriptions:
            if event.type() == QEvent.Type.Enter:
                self.show_shape_window(self.descriptions[source])
            elif event.type() == QEvent.Type.Leave:
                self.shape_window.hide()
        return super().eventFilter(source, event)

    def show_shape_window(self, text):
        """Показывает фигуру с текстом справа от главного окна."""
        self.shape_window.update_text(text)

        # Расчет позиции для окна-формы
        x = self.geometry().x() + self.width()  # Правый край главного окна
        y = self.geometry().y() + self.height() // 2 - self.shape_window.height() // 2

        self.shape_window.move(x, y)
        self.shape_window.show()

    def open_multyquery(self):
        self.hide()
        self.w = WindowMultyQuery(self.count_queries,self.id_person)
        self.w.show()
    def open_singlequery(self):
        from single_query import WindowSingleQuery
        self.close()
        self.w = WindowSingleQuery(self.count_queries, self.id_person)
        self.w.show()

    def open_route_parser(self):
        from yandex_route_window import WindowYandexRoute
        self.close()
        self.w = WindowYandexRoute(self.count_queries, self.id_person)
        self.w.show()
    def open_gis_jkh(self):
        from MKD_IJS_Window import WindowGisJkh
        self.close()
        self.w = WindowGisJkh(self.count_queries, self.id_person)
        self.w.show()
    def open_narod_yandex(self):
        from yandex_narod_window import NarodWidget
        self.close()
        self.w = NarodWidget(self.count_queries, self.id_person)
        self.w.show()

    def open_geocheki(self):
        from geocheki_window import GeochecksWidget
        self.close()
        self.w = GeochecksWidget(self.count_queries, self.id_person)
        self.w.show()
    def get_all_queries(self):
        self.all_queries = WindowAuth.get_all_queries()
        return self.all_queries

        # self.all_queries = self.thread.get_all_queries()

    def setUpMainWindow(self):
        header_label = QLabel(f"У вас {self.count_queries} запросов")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Выберете способ выгрузки")
        question_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_v_box = QVBoxLayout()
        self.main_v_box.addWidget(header_label)
        self.main_v_box.addWidget(question_label)

        # Список кнопок с описаниями
        buttons_info = [
            ("По одному элементу", self.open_singlequery, "Выгружайте с 2ГИС по одному элементу"),
            ("Многостраничная выгрузка", self.open_multyquery, "Выгружайте несколько страниц элементов с 2ГИС"),
            ("Выгрузка маршрутов", self.open_route_parser, "Выгружайте трассировку маршрутов с Яндекс.Карт"),
            ("Выгрузка МКД/ИЖС", self.open_gis_jkh, "Информация о застройке с портала ГИС ЖКХ. \n \n "
                                                    "- выберете целевую папку, куда будут загружены данные  \n"
                                                    "- подгрузите список городов в регионе (может занять до 5 минут) и выберите необходимые, либо  введите нужный город самостоятельно \n"
                                                    "- нажмите получить дома \n"),
            ("Выгрузка Народной карты", self.open_narod_yandex, "Выгружайте геометрии и типы объектов с Народной карты Яндекса \n \n"
                                                                "- установите целефую папку и координаты интересующей местности\n"
                                                                "- если программа запущена впервые, то введите свою учетную запись в Яндексе\n"
                                                                "- когда появится народная карта, то каждые 15 секунд в целевую папку будут добавлены объекты объекты, на которые будет наведен курсор мышки \n"
                                                                "- чтобы завершить парсинг нажмите СТОП в интерфейсе программы или просто закройте её "),
            ("Выгрузка геочеков", self.open_geocheki, "Описание для геочеков"),
        ]

        for text, callback, description in buttons_info:
            button = QPushButton(text)
            button.clicked.connect(callback) #вызов функции в buttons_info
            button.installEventFilter(self)  # Установка фильтра событий для кнопки
            self.main_v_box.addWidget(button)
            self.descriptions[button] = description  # Сохраняем описание для каждой кнопки

        self.setLayout(self.main_v_box)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

