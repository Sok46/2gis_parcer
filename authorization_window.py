import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,
                             QCheckBox, QFileDialog,QHBoxLayout,QProgressBar)
from PyQt6.QtGui import QFont, QPixmap, QAction, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal
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

        self.prog_bar = QProgressBar()
        # button_group.addButton(self.prog_bar)
        # self.main_v_box.addWidget(self.second_button)
        self.main_v_box.addWidget(self.prog_bar)


        self.easy_button = QPushButton('Войти без авторизации')
        button_group.addButton(self.easy_button)
        # self.main_v_box.addWidget(self.second_button)
        self.main_v_box.addLayout(self.ending_h_box)
        self.ending_h_box.addWidget(self.easy_button)




        # self.main_v_box.addWidget(self.confirm_button)
        # self.main_v_box.addWidget(self.back_button)
        self.setLayout(self.main_v_box)

        # seach_action.triggered.connect(self.save_file)
        self.show_password_cb.toggled.connect(self.displayPasswordIfChecked)
        self.login_button.pressed.connect(self.start_thread)
        # self.login_button.pressed.connect(self.checkAutorization)
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

    def changeLoginButtStatus(self):
        # self.login_button.setText("Ожидайте...")
        self.login_button.setEnabled(False)
        # if self.login_button.text() == "Ожидайте...":
        #
        self.checkAutorization()

    def checkAutorization(self):

        from add_pass_to_base import BasePassParcer
        self.google_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        sh: Spreadsheet = gc.open_by_url(self.google_sheet_url)
        ws = sh.sheet1

        pass_base = BasePassParcer.verify_person(self,ws,"yulia")

        if self.pass_text.text() == pass_base:
            print("Verno")
        else:
            print("Neverno")
            self.login_button.setEnabled(True)
            self.login_button.setText("Войти")



    def openMainWithLogin(self):
        from main_window import MainWindow

        self.close()
        self.w = MainWindow()
        self.w.show()

    def start_thread(self):

        self.thread = ThreadClass(self.pass_text.text(), self.login_button, self.login_text)

        self.thread.any_signal.connect(self.update_progress_bar)
        self.thread.accept_signal.connect(self.openMainWithLogin)

        self.thread.start()

    def update_progress_bar(self, value):
        self.prog_bar.setValue(value)



    def openMainEasy(self):
        from main_window import MainWindow
        self.close()
        self.w = MainWindow()
        self.w.show()

class ThreadClass(QThread):
    any_signal = pyqtSignal(int)
    accept_signal = pyqtSignal(int)

    def __init__(self, password, button, user_name, parent=None):
        super(ThreadClass, self).__init__(parent)
        self.is_running = True
        self.password = password
        self.button = button
        self.user_name = user_name.text()






    def run(self):
        self.button.setEnabled(False)
        self.button.setText("Ожидайте")


        cnt = 0

        from add_pass_to_base import BasePassParcer
        self.google_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        cnt = 10
        self.any_signal.emit(cnt)
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        sh: Spreadsheet = gc.open_by_url(self.google_sheet_url)
        ws = sh.sheet1

        pass_base = BasePassParcer.verify_person(self, ws, self.user_name)
        cnt = 50
        self.any_signal.emit(cnt)


        if self.password == pass_base:
            print("Verno")
            cnt = 100
            self.any_signal.emit(cnt)
            self.accept_signal.emit(cnt)

        else:
            cnt = 90
            self.any_signal.emit(cnt)
            print("Neverno")
            self.button.setEnabled(True)
            self.button.setText("Войти")
            cnt = 0
            self.any_signal.emit(cnt)


        # while self.is_running and cnt <= 100:
        #     cnt += 1
        #
        #     time.sleep(0.1)
        #     if cnt == 100:
        #         break

    def stop(self):
        self.is_running = False
        self.terminate()


    def stop(self):
        self.is_running = False
        print('stop thread...', self.index)
        self.terminate()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowSingleQuery()
    sys.exit(app.exec())



