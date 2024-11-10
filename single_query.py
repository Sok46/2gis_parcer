import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,
                              QFileDialog,QHBoxLayout,QGroupBox,QMessageBox)
from PyQt6.QtGui import QFont, QIcon, QWindow
from PyQt6.QtCore import Qt
from selenium.webdriver.chrome.options import Options
import datetime

import gspread
from gspread import Cell, Client, Spreadsheet, Worksheet

import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

from add_pass_to_base import BasePassParcer
from query_setter import QuerySetter

# import win32con
# import win32gui




class WindowSingleQuery(QWidget):
    def __init__(self,count_queries=5000,id_person=10):
        super().__init__()
        self.count_queries = int(count_queries)
        self.id_person = id_person
        self.my_base = BasePassParcer()
        self.driver = None

        # print(int(self.winId()))


        self.initializeUI()
        self.google_sheet_login()

    def google_sheet_login(self):
        self.googe_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        self.sh: Spreadsheet = gc.open_by_url(self.googe_sheet_url)
        self.ws = self.sh.sheet1

    def initializeUI(self):
        """Set up the application's GUI."""
        # self.setMaximumSize(310, 130)
        self.setWindowTitle("Urban parser | Выборочная выгрузка")
        self.setUpMainWindow()
        self.show()




    def checkboxClicked(self, button):
        """Проверяет, был ли нажат QCheckBox в группе кнопок."""
        print(button.text())
        self.confirm_button.setEnabled(True)

    def openBrowser(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)

        self.driver = webdriver.Chrome(options=chrome_options)
        # self.driver.minimize_window()
        url = 'https://2gis.ru/moscow/search/Шины'
        # self.link_url.setReadOnly(True)


        self.driver.get(url)

        # print("selenium handle", self.driver.current_window_handle)
        # print("selenium handle", self.driver.execute_script("return window.document.title"))
        # print("selenium handle", self.driver.execute_script("return window.name"))
        self.parce_button.setEnabled(True)
        self.browser_button.setEnabled(False)
        # win32gui.EnumWindows(self._enumWindows, None)


        # self.main_v_box.removeWidget(self.save_button)
        # self.main_v_box.removeWidget(self.browser_button)
    # def _enumWindows(self, hwnd, _):
    #     # if hwnd == self.myhwnd:
    #     #     return
    #     if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
    #         phwnd = win32gui.GetParent(hwnd)
    #         title = win32gui.GetWindowText(hwnd)
    #         name = win32gui.GetClassName(hwnd)
    #         # GetDoubleClickTime = win32gui.GetDoubleClickTime(hwnd)
    #
    #         if 'Шины в Москве' in title:
    #             print('{0}|{1}|\tЗаголовок：{2}\t|\Класс: {3}'.format(hwnd, phwnd, title, name))
    #             # my_window = hwnd
    #             my_window, phwnd = hwnd, phwnd
    #             # self.windowList.append(
    #             #     '{0}|{1}|\tЗаголовок：{2}\t|\Класс: {3}'.format(hwnd, phwnd, title, name))
    #
    #             style = win32gui.GetWindowLong(my_window, win32con.GWL_STYLE)
    #             exstyle = win32gui.GetWindowLong(my_window, win32con.GWL_EXSTYLE)
    #             # print('save', my_window, style, exstyle)
    #
    #             widget = QWidget.createWindowContainer(QWindow.fromWinId(my_window))
    #             widget.setMinimumSize(1200,700)
    #             # widget.setFixedHeight(400)
    #             # widget.setFixedWidth(800)
    #             # widget.setWidgetResizable(True)
    #             widget.my_window = my_window
    #             widget.phwnd = phwnd
    #             widget.style = style
    #             widget.exstyle = exstyle
    #             widget.setParent(self)
    #             # layout = QVBoxLayout()
    #             # layout.addWidget(widget)
    #             self.main_h_box.addWidget(widget)

    def stopDriver(self):
        self.driver.quit()

    def prnt(self):
        print('Спарсить')

    def parceElement(self):
        print("!!!")
        if self.count_queries < 1:
            self.parce_button.setEnabled(False)
            self.header_label.setStyleSheet("color: red;")
            return


        points = []
        ulitsa = []
        geos = []
        arr_lat = []
        arr_long = []
        arr_stars = []
        arr_voices = []
        type_arr = []


        def find_item(by_method, value):
            try:
                if by_method == 'class':
                    item = self.driver.find_element(By.CLASS_NAME, value)
                elif by_method == 'css':
                    item = self.driver.find_element(By.CSS_SELECTOR, value)
            except:
                item = 'error'
            try:
                item = item.text
            except:
                item = 'error'
            return item

        name = find_item('class', '_cwjbox')
        type_item = find_item('class', '_1idnaau')
        street = find_item('css',
                           '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1b96w9b > div:nth-child(2) > div._t0tx82 > div._8sgdp4 > div > div:nth-child(1) > div._49kxlr > div > div:nth-child(2) > div:nth-child(1) > span')
        descr = find_item('css', '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1b96w9b > div:nth-child(2) > div._t0tx82 > div._8sgdp4 > div > div:nth-child(1) > div._49kxlr > div > div:nth-child(2) > div:nth-child(1) > div')
        stars = find_item('css',
                          '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._146hbp5 > div > div._y10azs')
        count_voices = find_item('css',
                                 '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._146hbp5 > div > div._jspzdm')

        lat_right = str(self.driver.current_url).split('.')[2].split('&')[0].split('?')[0].split('%')[0]
        # print(lat_right)
        lat_left = str(self.driver.current_url).split('.')[1][-2:]
        lat = str(lat_left) + '.' + str(lat_right)

        long_right = str(self.driver.current_url).split('.')[3].split('&')[0].split('?')[0].split('%')[0]
        long_left = str(self.driver.current_url).split('.')[2][-2:]

        long = str(long_left) + '.' + str(long_right)

        print(lat, long)
        type_arr.append(type_item)
        arr_lat.append(lat)
        arr_long.append(long)

        geos.append(descr)
        ulitsa.append(street)
        arr_stars.append(stars)
        arr_voices.append(count_voices)
        points.append(name)

        df = pd.DataFrame({'name': points, 'type': type_arr, 'descr': geos, 'ulitsa': ulitsa, 'stars': arr_stars,
                           'count_voices': arr_voices, 'lat': arr_lat, 'long': arr_long})

        if os.path.isfile(self.link_url.text()):  # ставить или не ставить headers
            head = False
        else:
            head = True


        self.count_queries -= 1



        if self.my_base.set_queries(self.ws,int(self.id_person), self.sh, int(self.count_queries)): # проверка на существоваение id пользователя
            df.to_csv(self.link_url.text(), sep=';',
                      encoding='utf8', index=False, mode='a', header=head)
            self.header_label.setText(f"У вас {self.count_queries} запросов")
        else:
            print("Нет юзера")
            self.header_label.setText(f"Юзера не существует")
            self.header_label.setStyleSheet("color: red;")
            # self.count_queries = 0
            # self.driver.close()

    def enabledUrlButt(self):
        # self.browser_button.setEnabled(True)
        self.len_url = len(self.link_url.text())
        print(self.len_url)
        if self.len_url > 5:
            self.browser_button.setEnabled(True)
        else:
            self.browser_button.setEnabled(False)



    def save_file(self):
        f_dialog = QFileDialog().getSaveFileName(self, "Save File", "парсинг 2гис", "csv Files (*.csv)")
        path = f_dialog[0]
        self.link_url.setText(path)

    def open_main(self):
        from main_window import MainWindow
        self.close()
        self.w = MainWindow(self.count_queries)
        self.w.show()
        # self.driver.
        # if self.driver:
        #     self.driver.close()

    def show_window_2(self):
        from multy_query import WindowMultyQuery
        self.close()
        # if self.driver:
        #     self.driver.close()
        self.w = WindowMultyQuery(self.count_queries)
        self.w.show()

    def closeEvent(self, event): #Зарезервированный метод на закрытие программы
        reply = QMessageBox.question(
            self,
            'Подтверждение выхода',
            'Вы уверены, что хотите закрыть программу?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()  # Если пользователь нажал "Да", закрываем приложение


            # if self.driver:
            #     self.driver.close()
            self.close()
        else:
            event.ignore()




    def setUpMainWindow(self):
        self.len_url = 0
        self.filename = datetime.datetime.now()
        """Создайте и расположите виджеты в главном окне."""
        self.header_label = QLabel(f"У вас {self.count_queries} запросов")
        self.header_label.setFont(QFont("Arial", 18))
        self.header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Выберете действие")
        question_label.setAlignment(Qt.AlignmentFlag.AlignBottom)

        button_group = QButtonGroup(self)
        button_group.buttonClicked.connect(
            self.checkboxClicked)

        self.confirm_button = QPushButton("Завершить программу")
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self.stopDriver)
        self.confirm_button.clicked.connect(self.close)


        self.back_button = QPushButton("Назад")
        self.back_button.setEnabled(True)
        # self.confirm_button.clicked.connect(self.stopDriver)
        # self.confirm_button.clicked.connect(self.close)

        self.main_v_box = QVBoxLayout()
        self.main_h_box = QHBoxLayout()
        self.widgets_group = QGroupBox()
        self.widgets_group.setFixedWidth(300)
        self.main_v_box.addWidget(self.header_label)
        self.main_v_box.addWidget(question_label)

        self.ending_h_box = QHBoxLayout()

        self.link_url = QLineEdit()
        # self.link_url.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.link_url.setClearButtonEnabled(True)
        # self.link_url.addAction(QIcon('icons/folder_icon.png'), QLineEdit.ActionPosition.LeadingPosition)
        seach_action = self.link_url.addAction(QIcon('icons/folder_icon.png'),QLineEdit.ActionPosition.LeadingPosition)

        self.link_url.setPlaceholderText('Укажите путь для выходного csv ...')
        self.main_v_box.addWidget(self.link_url)

        self.browser_button = QPushButton("Открыть браузер")
        button_group.addButton(self.browser_button)
        self.browser_button.setEnabled(True)
        self.main_v_box.addWidget(self.browser_button)


        self.parce_button = QPushButton("Спарсить элемент")
        button_group.addButton(self.parce_button)
        self.parce_button.setEnabled(False)
        self.main_v_box.addWidget(self.parce_button)



        self.second_button = QPushButton('Многостраничная выгрузка')
        button_group.addButton(self.second_button)
        # self.main_v_box.addWidget(self.second_button)
        self.main_v_box.addLayout(self.ending_h_box)
        self.ending_h_box.addWidget(self.second_button)
        self.ending_h_box.addWidget(self.back_button)


        self.main_v_box.addWidget(self.confirm_button)
        self.widgets_group.setLayout(self.main_v_box)
        self.widgets_group.setFixedHeight(220)

        self.main_h_box.addWidget(self.widgets_group)
        # self.main_v_box.addWidget(self.back_button)
        self.setLayout(self.main_h_box)

        seach_action.triggered.connect(self.save_file)
        self.back_button.clicked.connect(self.open_main)
        self.browser_button.clicked.connect(self.openBrowser)
        self.link_url.textChanged.connect(self.enabledUrlButt)
        self.parce_button.clicked.connect(self.parceElement)
        self.second_button.clicked.connect(self.show_window_2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowSingleQuery()
    sys.exit(app.exec())
