import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,QHBoxLayout)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
from multy_query import WindowMultyQuery
from Urban_parser import WindowAuth


class MainWindow(QWidget):
    def __init__(self, count_queries = 0, id_person = 10):
        super().__init__()
        self.count_queries = count_queries
        self.id_person = id_person

        self.initializeUI()

    def initializeUI(self):
        """Set up the application's GUI."""
        # self.setMaximumSize(310, 130)
        self.setWindowTitle("Urban parser")
        self.setUpMainWindow()
        self.show()

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
    def get_all_queries(self):
        self.all_queries = WindowAuth.get_all_queries()
        return self.all_queries

        # self.all_queries = self.thread.get_all_queries()

    def setUpMainWindow(self):
        header_label = QLabel(f"У вас {self.count_queries} запросов")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Выберете способ выгрузки")
        question_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        button_group = QButtonGroup(self)

        self.main_v_box = QVBoxLayout()
        self.main_v_box.addWidget(header_label)
        self.main_v_box.addWidget(question_label)

        self.main_h_box = QHBoxLayout()

        self.save_path_textedit = QLineEdit()
        # self.link_url.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.save_path_textedit.setClearButtonEnabled(True)
        # self.link_url.addAction(QIcon('icons/folder_icon.png'), QLineEdit.ActionPosition.LeadingPosition)
        seach_action = self.save_path_textedit.addAction(QIcon('icons/folder_icon.png'),
                                                         QLineEdit.ActionPosition.LeadingPosition)


        self.single_button = QPushButton("По одному элементу")
        button_group.addButton(self.single_button)
        self.single_button.setEnabled(True)
        self.main_v_box.addWidget(self.single_button)



        self.multy_button = QPushButton("Многостраничная выгрузка")
        button_group.addButton(self.multy_button)
        self.multy_button.setEnabled(True)
        self.main_v_box.addWidget(self.multy_button)

        self.route_button = QPushButton("Выгрузка марштуров общественного транспорта")
        button_group.addButton(self.route_button)
        self.main_v_box.addWidget(self.route_button)

        self.houses_button = QPushButton("Выгрузка МКД/ИЖС")
        button_group.addButton(self.houses_button)
        self.main_v_box.addWidget(self.houses_button)

        self.narod_button = QPushButton("Выгрузка Народной карты")
        button_group.addButton(self.narod_button)
        self.main_v_box.addWidget(self.narod_button)

        self.setLayout(self.main_v_box)
        self.single_button.clicked.connect(self.open_singlequery)
        self.houses_button.clicked.connect(self.open_gis_jkh)
        # self.link_url.textChanged.connect(self.enabledUrlButt)
        self.multy_button.clicked.connect(self.open_multyquery)
        self.route_button.clicked.connect(self.open_route_parser)
        self.narod_button.clicked.connect(self.open_narod_yandex)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

