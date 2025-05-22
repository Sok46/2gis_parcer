import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,QHBoxLayout,QSpinBox,QFileDialog)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QTimer
from add_pass_to_base import BasePassParcer
from gspread import Client, Spreadsheet
import gspread
import time
from loading_window import LoadingWindow
import os

class MyWidget(QWidget):
    def __init__(self,count_queries = 25, id_person = 10, price_query = 15):
        super().__init__()

        self.priceQuery = price_query
        self.count_queries = int(count_queries)
        self.id_person = id_person
        self.my_base = BasePassParcer()
        self.loading_window = LoadingWindow(self)

        self.initializeUI()
        self.google_sheet_login()

        self.stage = 0
    def save_file(self):
        f_dialog = QFileDialog().getExistingDirectory()
        # f_dialog = QFileDialog().getSaveFileName(self, "Save File", "парсинг 2гис", "csv Files (*.csv)")
        path = f_dialog
        self.save_path_textedit.setText(path)
    def open_main(self):
        from main_window import MainWindow
        self.loading_window = LoadingWindow()  # Создаем новое окно каждый раз
        self.loading_window.show()
        QApplication.processEvents()  # Обрабатываем события, чтобы окно загрузки отобразилось
        QTimer.singleShot(100, lambda: self._complete_switch(MainWindow, self.count_queries, self.id_person))

    def _complete_switch(self, window_class, *args):
        self.w = window_class(*args)
        self.w.show()
        self.hide()
        if hasattr(self, 'loading_window'):
            self.loading_window.close()

    def google_sheet_login(self):
        self.googe_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        gc: Client = gspread.service_account(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "google_service_account.json"))
        self.sh: Spreadsheet = gc.open_by_url(self.googe_sheet_url)
        self.ws = self.sh.sheet1

    def initializeUI(self):
        """Set up the application's GUI."""
        # self.setMaximumSize(310, 130)
        self.setWindowTitle("Urban parser | Выгрузка маршрутов")
        self.setUpMainWindow()
        self.show()

    def change_directory(self):
        if len(self.save_path_textedit.text()) > 3:
            # self.scroll.setEnabled(True)
            # self.confirm_button.setEnabled(True)
            # self.browser_button.setEnabled(True)
            try:
                self.cityname_textedit.setEnabled(True)
                if len(self.cityname_textedit.text()) > 3: #Если город введен вручную
                    self.stage = 1
                    self.browser_button.setEnabled(True)
            except:
                self.browser_button.setEnabled(True)

            # elif self.checked_cities and len(self.checked_cities) > 0: #Если выбран
            #     self.stage = 2
            #     self.browser_button.setEnabled(True)
            # else:
            #     self.browser_button.setEnabled(False)

        else:
            self.stage = 0
            # self.scroll.setEnabled(False)
            self.confirm_button.setEnabled(False)
            self.browser_button.setEnabled(False)
            self.cityname_textedit.setEnabled(False)

    def setUpMainWindow(self):
        self.coinIcon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "coin.png")
        self.coinIcon = QIcon(self.coinIcon_path)
        self.header_label = QLabel(
            f'У вас {self.count_queries} <img src={self.coinIcon_path} width="30" height="30" style="vertical-align: top;">'
        )

        self.header_label.setFont(QFont("Arial", 14))
        self.header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Укажите путь...")
        question_label.setAlignment(Qt.AlignmentFlag.AlignBottom)

        button_group = QButtonGroup(self)
        # button_group.buttonClicked.connect(
        #     self.checkboxClicked)

        self.confirm_button = QPushButton("Завершить программу")
        self.confirm_button.setEnabled(False)

        # self.confirm_button.clicked.connect(self.stopDriver)
        # self.confirm_button.clicked.connect(self.close)

        self.back_button = QPushButton("Назад")
        self.back_button.setEnabled(True)


        self.main_v_box = QVBoxLayout()
        self.main_v_box.addWidget(self.header_label)
        self.main_v_box.addWidget(question_label)

        self.main_h_box = QHBoxLayout()
        self.back_h_box = QHBoxLayout()

        self.save_path_textedit = QLineEdit()
        # self.link_url.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.save_path_textedit.setClearButtonEnabled(True)
        # self.link_url.addAction(QIcon('icons/folder_icon.png'), QLineEdit.ActionPosition.LeadingPosition)
        seach_action = self.save_path_textedit.addAction(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "folder_icon.png")), QLineEdit.ActionPosition.LeadingPosition)

        self.save_path_textedit.setPlaceholderText('Укажите путь для выходного файла ...')
        self.main_v_box.addWidget(self.save_path_textedit)

        self.cityname_label = QLabel("Название города (и субъект)*")
        self.cityname_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_v_box.addWidget(self.cityname_label)
        self.cityname_textedit = QLineEdit()
        self.cityname_textedit.setPlaceholderText("Бородино, Красноярский край")
        self.main_v_box.addWidget(self.cityname_textedit)


        self.browser_button = QPushButton(f"Начать парсинг   ({self.priceQuery})")
        self.browser_button.setIcon(self.coinIcon)
        self.browser_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Иконка справа

        self.browser_button.setEnabled(False)
        self.main_v_box.addWidget(self.browser_button)
        self.main_v_box.addWidget(self.back_button)

        self.setLayout(self.main_v_box)

        seach_action.triggered.connect(self.save_file)
        self.back_button.clicked.connect(self.open_main)
        self.cityname_textedit.textChanged.connect(self.change_directory)
        self.save_path_textedit.textChanged.connect(self.change_directory)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWidget()
    sys.exit(app.exec())