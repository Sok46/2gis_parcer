import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,
                             QCheckBox, QFileDialog)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from selenium.webdriver.chrome.options import Options
import datetime

import time

import pandas as pd

from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
import threading


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initializeUI()

    def initializeUI(self):
        """Set up the application's GUI."""
        # self.setMaximumSize(310, 130)
        self.setWindowTitle("QPushButton Example")
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
        # url = input('вставьте ссылку на карту: ')
        url = self.link_url.text()
        self.link_url.setReadOnly(True)
        self.driver.get(url)
        self.parce_button.setEnabled(True)
        self.browser_button.setEnabled(False)

        # self.main_v_box.removeWidget(self.save_button)
        # self.main_v_box.removeWidget(self.browser_button)

    def stopDriver(self):
        self.driver.quit()

    def prnt(self):
        print('Спарсить')

    def parceElement(self):
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

        name = find_item('class', '_tvxwjf')
        type_item = find_item('class', '_1idnaau')
        street = find_item('css',
                           '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1b96w9b > div:nth-child(2) > div._t0tx82 > div._8sgdp4 > div > div:nth-child(1) > div._49kxlr > div > div:nth-child(2) > div:nth-child(1)')
        descr = find_item('class', '_1p8iqzw')
        stars = find_item('css',
                          '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._146hbp5 > div > div._y10azs')
        count_voices = find_item('css',
                                 '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._146hbp5 > div > div._jspzdm')

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
        # path = fr'C:\Users\sergey.biryukov\Desktop\Москва генплан конкурс\Общепит/blya.csv'
        if os.path.isfile(self.path):  # ставить или не ставить headers
            head = False
        else:
            head = True
        df.to_csv(self.path, sep=';',
                  encoding='utf8', index=False, mode='a', header=head)
        print(111)

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
        self.path = f_dialog[0]

    def setUpMainWindow(self):
        self.len_url = 0
        self.filename = datetime.datetime.now()
        """Создайте и расположите виджеты в главном окне."""
        header_label = QLabel("2GIS_Parcer by Sergey_Biryukov")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Выберете действие")
        question_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        button_group = QButtonGroup(self)
        button_group.buttonClicked.connect(
            self.checkboxClicked)

        self.confirm_button = QPushButton("Завершить программу")
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self.stopDriver)
        self.confirm_button.clicked.connect(self.close)

        self.main_v_box = QVBoxLayout()
        self.main_v_box.addWidget(header_label)
        self.main_v_box.addWidget(question_label)


        self.save_button = QPushButton("Установить путь выходного файла...")
        button_group.addButton(self.save_button)
        self.save_button.clicked.connect(self.save_file)
        self.main_v_box.addWidget(self.save_button)

        self.link_url = QLineEdit()

        # self.link_url.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.link_url.setClearButtonEnabled(True)
        self.link_url.setPlaceholderText('Вставьте ссылку на 2ГИС с элементами для парсинга')
        self.main_v_box.addWidget(self.link_url)

        self.browser_button = QPushButton("Открыть браузер")
        button_group.addButton(self.browser_button)
        self.browser_button.setEnabled(False)
        self.main_v_box.addWidget(self.browser_button)


        self.parce_button = QPushButton("Спарсить элемент")
        button_group.addButton(self.parce_button)
        self.parce_button.setEnabled(False)
        self.main_v_box.addWidget(self.parce_button)

        self.main_v_box.addWidget(self.confirm_button)
        self.setLayout(self.main_v_box)

        self.browser_button.clicked.connect(self.openBrowser)
        self.link_url.textChanged.connect(self.enabledUrlButt)
        self.parce_button.clicked.connect(self.parceElement)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
