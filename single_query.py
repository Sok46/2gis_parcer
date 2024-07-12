import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,QLineEdit,QButtonGroup,QVBoxLayout,QCheckBox)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from selenium.webdriver.chrome.options import Options


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
        url = input('вставьте ссылку на карту: ')

        self.driver.get(url)

    def stopDriver(self):
        self.driver.quit()

    def prnt(self):
        print('Спарсить')


    def setUpMainWindow(self):
        """Создайте и расположите виджеты в главном окне."""
        header_label = QLabel("2GIS_Parcer by Sergey_Biryukov")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(
        Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Выберете действие")
        question_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ratings = ["Открыть браузер", "Спарсить элемент"]
        button_group = QButtonGroup(self)
        button_group.buttonClicked.connect(
            self.checkboxClicked)

        self.confirm_button = QPushButton("Завершить программу")
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self.stopDriver)
        self.confirm_button.clicked.connect(self.close)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(header_label)
        main_v_box.addWidget(question_label)


        self.browser_button = QPushButton("Открыть браузер")
        button_group.addButton(self.browser_button)
        self.browser_button.clicked.connect(self.openBrowser)
        main_v_box.addWidget(self.browser_button)
        main_v_box.addWidget(self.confirm_button)
        self.setLayout(main_v_box)

        self.parce_button = QPushButton("Спарсить элемент")
        button_group.addButton(self.parce_button)
        self.parce_button.clicked.connect(self.prnt)
        main_v_box.addWidget(self.parce_button)
        main_v_box.addWidget(self.confirm_button)
        self.setLayout(main_v_box)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())