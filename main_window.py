import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup,QHBoxLayout, QVBoxLayout,QFrame)
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

        self.shape_window.move(20 + x, y)
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
        self.w = WindowYandexRoute(self.count_queries, self.id_person, 25)
        self.w.show()
    def open_gis_jkh(self):
        from MKD_IJS_Window import WindowGisJkh
        self.close()
        self.w = WindowGisJkh(self.count_queries, self.id_person)
        self.w.show()
    def open_narod_yandex(self):
        from yandex_narod_window import NarodWidget
        self.close()
        self.w = NarodWidget(self.count_queries, self.id_person,30)
        self.w.show()

    def open_geocheki(self):
        from geocheki_window import GeochecksWidget
        self.close()
        self.w = GeochecksWidget(self.count_queries, self.id_person, 50)
        self.w.show()
    def get_all_queries(self):
        self.all_queries = WindowAuth.get_all_queries()
        return self.all_queries
    # def dvaGis_show(self):


        # self.all_queries = self.thread.get_all_queries()

    def setUpMainWindow(self):
        header_label = QLabel(f"У вас {self.count_queries} запросов")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Выберете способ выгрузки")
        question_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.dvaGis_frame = QFrame()
        self.dvaGis_frame.hide()
        self.dvaGis_frame.setFrameShape(QFrame.Shape.Box)  # Устанавливаем форму рамки
        # dvaGis_frame.setLineWidth(1)  # Устанавливаем ширину линии рамки
        dvaGis_icon = QIcon(
            fr"icons\2gis_logo.png")  # Укажите путь к вашему изображению
        # dvaGis_icon.pixmap(32, 32)
        # Создаем QLabel для иконки
        icon_label = QLabel()
        icon_pixmap = dvaGis_icon.pixmap(32, 32)  # Устанавливаем размер иконки
        icon_label.setPixmap(icon_pixmap)
        dvaGis_label = QLabel('<div style="text-align: left;  margin-bottom: 0px;"><a href="https://github.com/interlark/parser-2gis/releases/tag/v1.2.1">2ГИС лучше выгружать по ссылке</a>'
                              '</div>')

        dvaGis_label.setTextFormat(Qt.TextFormat.RichText)  # Устанавливаем формат текста как RichText
        dvaGis_label.setOpenExternalLinks(True)  # Позволяет открывать ссылки в браузере
        dvaGis_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        dvaGis_label.setWindowIcon(dvaGis_icon)

        dvaGis_button = QPushButton('Выгрузка 2ГИС')
        dvaGis_button.setIcon(dvaGis_icon)
        dvaGis_button.clicked.connect(self.dvaGis_frame.show)

        self.h_widget = QWidget()
        self.main_v_box = QVBoxLayout()
        self.main_v_box.setSpacing(0)
        self.dvaGis_v_box = QVBoxLayout()
        self.dvaGis_h_box = QHBoxLayout()
        self.dvaGis_h_box.addWidget(dvaGis_button)
        self.dvaGis_h_box.addWidget(dvaGis_label)
        self.h_widget.setLayout(self.dvaGis_h_box)
        # self.dvaGis_v_box.addWidget(icon_label)
        # self.dvaGis_v_box.addWidget(dvaGis_label)
        self.dvaGis_v_box.setSpacing(0)


        self.main_v_box.addWidget(header_label)
        self.main_v_box.addWidget(question_label)

        dvaGis_widget = QWidget()
        self.dvaGis_frame.setLayout(self.dvaGis_v_box)
        # dvaGis_widget.setLayout(self.dvaGis_v_box)

        # self.main_v_box.addWidget(dvaGis_label)


        # Список кнопок с описаниями
        buttons_info = [
            ("По одному элементу", self.open_singlequery, """
                                                                <div style="text-align: center; font-size: 14px; font-weight: bold; margin-bottom: 2px;">
                                                                    Выгружайте точки интереса по одному элементу 
                                                                </div>
                                                                <div style="text-align: left; font-size: 7 px; margin-left: 8px;">
                                                                    <p>- Выберете целевую папку, куда будут загружены данные</p>
                                                                    <p >- откройте браузер через интерфейс программы</p>
                                                                    <p>- Введите поисковой запрос, который вас интересует</p>
                                                                    <p>- Нажмите на интересующий элемент в окне браузера слева </p>
                                                                    <p>- Нажмите "Спарсить элемент" </p>
                                       
                                                                </div>
                                                                """),
            ("Многостраничная выгрузка", self.open_multyquery, """
                                                                <div style="text-align: center; font-size: 14px; font-weight: bold; margin-bottom: 2px;">
                                                                    Выгружайте точки интереса постранично 
                                                                </div>
                                                                <div style="text-align: left; font-size: 7 px; margin-left: 8px;">
                                                                    <p style="margin: 1.5;">- Выберете целевую папку, куда будут загружены данные</p>
                                                                    <p style="margin: 1.5;">- откройте браузер через интерфейс программы</p>
                                                                    <p style="margin: 1.5;">- Введите поисковой запрос, который вас интересует</p>
                                                                    <p style="margin: 1.5;">- Убедитесь, что поисковой запрос содержит более 1 страницы результатов </p>
                                                                    <p style="margin: 1.5;">- НАЖМИТЕ НА ЛЮБОЙ ЭЛЕМЕНТ ВЫДАЧИ БРАУЗЕРА </p>
                                                                    <p style="margin: 1.5;">- Установите необходимое количество страниц для парсинга в интерфейсе программы</p>
                                                                    <p style="margin: 1.5;">- Нажмите "Начать парсинг" и дождитесь его завершения, НЕДВИГАЯ МЫШЬЮ.</p>
                                       
                                                                </div>
                                                                """),
            ("Выгрузка маршрутов", self.open_route_parser, """
                                                                <div style="text-align: center; font-size: 14px; font-weight: bold; margin-bottom: 2px;">
                                                                    Выгрузка трассировки маршрутов с Яндекс.Карт 
                                                                </div>
                                                                <div style="text-align: left; font-size: 7 px; margin-left: 8px;">
                                                                    <p>- Выберете целевую папку, куда будут загружены данные</p>
                                                                    <p >- Укажите город (и субъект, если это необходимо)</p>
                                                                    <p>- Укажите номера маршрутов общественного танспорта для выгрузки (через запятую, игнорируя спецсимволы, например "/")</p>
                                                                    <p>- Нажмите "Начать парсинг" и подождите </p>
                                       
                                                                </div>
                                                                """),

            ("Выгрузка МКД/ИЖС", self.open_gis_jkh, """
                                                                <div style="text-align: center; font-size: 14px; font-weight: bold; margin-bottom: 2px;">
                                                                    Информация о застройке с портала  ГИС ЖКХ 
                                                                </div>
                                                                <div style="text-align: left; font-size: 11px; margin-left: 8px;">
                                                                    <p > 
                                                                    Получите данные о зданиях в выбранных населенных пунктах. 
                                                                    Атрибутивка включает в себя данные о жилой площади, количестве жилых помещений, аварийности зданий и др...
                                                                    Данные выгружаются в excel файлы без координатной привязки (необходимо геокодироание)
                                                                    </p>
                                                                    <p style="margin: 1;">- Выберете целевую папку, куда будут загружены данные</p>
                                                                    <p style="margin: 1;">- Подгрузите список городов в регионе (может занять до 5 минут), либо  введите нужный город самостоятельно</p>
                                                                    <p style="margin: 1;">- Нажмите "получить дома"</p>
                                                                    <p style="margin: 1;">- Выгрузка excel-файла может потребовать времени в зависимости от объема информации</p>
                                       
                                                                </div>
                                                                """),
            ("Выгрузка Народной карты", self.open_narod_yandex, """
                                                                <div style="text-align: center; font-size: 14px; font-weight: bold; margin-bottom: 2px;">
                                                                    Выгружайте геометрии и типы объектов с Народной карты Яндекса
                                                                </div>
                                                                <div style="text-align: left; font-size: 7 px; margin-left: 8px;">
                                                                    <p>- Установите целевую папку и координаты интересующей местности.</p>
                                                                    <p>- Если программа запущена впервые, введите свою учетную запись Яндекса и нажпите кнопку "Я авторизовался, запомни меня".</p>
                                                                    <p>- Когда появится Народная карта, каждые 15 секунд в целевую папку будут добавлены объекты, 
                                                                    на которые будет наведен курсор мышки.</p>
                                                                    <p>- Чтобы завершить парсинг, нажмите СТОП в интерфейсе программы или просто закройте её.</p>
                                                                </div>
                                                                """),
            ("Выгрузка геочеков ФНС", self.open_geocheki, """
                                                                <div style="text-align: center; font-size: 14px; font-weight: bold; margin-bottom: 2px;">
                                                                    Выгрузка информации о транзакциях с карты ФНС России
                                                                </div>
                                                                <div style="text-align: left; font-size: 7 px; margin-left: 8px;">
                                                                    <p>- Установите целевую папку для выгрузки гексов</p>
                                                                    <p>- Нажмите "начать парсинг".</p>
                                                                    <p>- Когда появится  карта, каждые 15 секунд в целевую папку будут добавлены гексоны,
                                                                    которые оказались в пределах видимости вашего экрана (водить по ним мышкой и щелкать не нужно).</p>
                                                                    <p>- Чтобы завершить парсинг, нажмите СТОП в интерфейсе программы или просто закройте её.</p>
                                                                </div>
                                                                """),
        ]
        # Устанавливаем иконку для кнопки

        i = 1
        for text, callback, description in buttons_info:
            button = QPushButton(text)
            button.clicked.connect(callback) #вызов функции в buttons_info
            button.installEventFilter(self)  # Установка фильтра событий для кнопки
            button.setStyleSheet("""
                                QPushButton {
                                    background-color: transparent;  /* Прозрачный фон */
                                    border: none;                  /* Убираем границу */
                                    padding: 5px 5px 5px 5px;
                                    font-size: 14px;              /* Увеличиваем размер шрифта */
                                }
                                QPushButton:hover {
                                    background-color: lightgray;   /* Опционально: цвет при наведении */
                                }
                            """)
            if i > 2:
                icon = QIcon(
                    fr"C:\Users\Sergey_Biryukov\Desktop\parcers\pythonProject\2gis_parcer\icons\main_buttons\{i}.png")  # Укажите путь к вашему изображению
                button.setIcon(icon)
                self.main_v_box.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
                # Убираем заливку с помощью стилей

            else:
                self.dvaGis_v_box.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
                # button.setStyleSheet("background-color: white; color: limegreen;")
                # button.setStyleSheet(" color: dimgrey;")

            self.descriptions[button] = description  # Сохраняем описание для каждой кнопки
            i+=1

        self.setLayout(self.main_v_box)
        self.main_v_box.addWidget(self.h_widget)
        self.main_v_box.addWidget(dvaGis_button)
        self.main_v_box.addWidget(self.dvaGis_frame)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

