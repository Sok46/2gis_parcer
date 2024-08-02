import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,
                             QCheckBox, QFileDialog,QHBoxLayout)
from PyQt6.QtGui import QFont, QPixmap, QAction, QIcon
from PyQt6.QtCore import Qt
from selenium.webdriver.chrome.options import Options
import datetime
import gspread
from gspread import Cell, Client, Spreadsheet, Worksheet


import time

import pandas as pd

from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from multy_query import WindowMultyQuery


import threading


class WindowSingleQuery(QWidget):
    def __init__(self):
        super().__init__()

        self.initializeUI()

    def initializeUI(self):
        """Set up the application's GUI."""
        # self.setMaximumSize(310, 130)
        self.setWindowTitle("2GIS parcer_by_Sergey_Biryukov")
        self.setUpMainWindow()
        self.show()




    def setUpMainWindow(self):
        self.len_url = 0
        self.filename = datetime.datetime.now()
        """Создайте и расположите виджеты в главном окне."""
        header_label = QLabel("2GIS_Parcer")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Выберете действие")
        question_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        button_group = QButtonGroup(self)
        # button_group.buttonClicked.connect(
        #     self.checkboxClicked)

        # self.confirm_button = QPushButton("Завершить программу")
        # self.confirm_button.setEnabled(False)
        # self.confirm_button.clicked.connect(self.stopDriver)
        # self.confirm_button.clicked.connect(self.close)


        # self.back_button = QPushButton("Назад")
        # self.back_button.setEnabled(True)
        # self.confirm_button.clicked.connect(self.stopDriver)
        # self.confirm_button.clicked.connect(self.close)

        self.main_v_box = QVBoxLayout()
        self.main_v_box.addWidget(header_label)
        self.main_v_box.addWidget(question_label)

        self.ending_h_box = QHBoxLayout()

        self.login_text = QLineEdit()
        # self.link_url.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.login_text.setClearButtonEnabled(True)

        self.login_text.setPlaceholderText('логин')
        self.main_v_box.addWidget(self.login_text)

        self.pass_text = QLineEdit()
        self.pass_text.setPlaceholderText('пароль')
        self.pass_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.main_v_box.addWidget(self.pass_text)

        self.show_password_cb = QCheckBox("Показать пароль", self)

        self.main_v_box.addWidget(self.show_password_cb)



        self.login_button = QPushButton("Войти")
        button_group.addButton(self.login_button)
        self.login_button.setEnabled(True)
        self.main_v_box.addWidget(self.login_button)


        self.easy_button = QPushButton('Войти без авторизации')
        button_group.addButton(self.easy_button)
        # self.main_v_box.addWidget(self.second_button)
        self.main_v_box.addLayout(self.ending_h_box)
        self.ending_h_box.addWidget(self.easy_button)
        # self.ending_h_box.addWidget(self.back_button)


        # self.main_v_box.addWidget(self.confirm_button)
        # self.main_v_box.addWidget(self.back_button)
        self.setLayout(self.main_v_box)

        # seach_action.triggered.connect(self.save_file)
        self.show_password_cb.toggled.connect(self.displayPasswordIfChecked)
        self.login_button.clicked.connect(self.checkAutorization)
        self.easy_button.clicked.connect(self.openMainEasy)

    def displayPasswordIfChecked(self, checked):
        """Если QCheckButton включен, просмотрите пароль.
        В противном случае замаскируйте пароль, чтобы другие
        не могли его увидеть."""
        if checked:
            self.pass_text.setEchoMode(
                QLineEdit.EchoMode.Normal)
        elif checked == False:
            self.pass_text.setEchoMode(
                QLineEdit.EchoMode.Password)

    def checkAutorization(self):
        print(111)
        from add_pass_to_base import BasePassParcer
        print(222)
        self.google_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        sh: Spreadsheet = gc.open_by_url(self.google_sheet_url)
        ws = sh.sheet1

        pass_base = BasePassParcer.verify_person(self,ws,"yulia")
        print(444)
        if self.pass_text.text() == pass_base:
            print("Verno")
        else:
            print("Neverno")


    def openMainWithLogin(self):
        from main_window import MainWindow
        self.close()
        self.w = MainWindow()
        self.w.show()

    def openMainEasy(self):
        from main_window import MainWindow
        self.close()
        self.w = MainWindow()
        self.w.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowSingleQuery()
    sys.exit(app.exec())
