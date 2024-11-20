import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,
                             QCheckBox,QHBoxLayout,QProgressBar)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import datetime
import gspread
from gspread import Client, Spreadsheet
import re
import json
import os


class WindowAuth(QWidget):
    def __init__(self):
        super().__init__()
        self.login_pass_dir = os.path.dirname(os.path.realpath(__file__))
        self.credentials_path = os.path.join(self.login_pass_dir, "credentials.json")

        self.initializeUI()

    def initializeUI(self):
        """Set up the application's GUI."""
        # self.setMaximumSize(310, 130)
        self.setWindowTitle("Urban parser")
        self.setUpMainWindow()
        self.show()

    def line_edit_rules(self, line_edit: QLineEdit): #Правила для ввода логина/пароля
        def is_valid_string(input_string):
            # Регулярное выражение для проверки: только латинские буквы и специальные символы
            pattern = r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};":\\|,.<>\/?]+$'
            return bool(re.match(pattern, input_string))
        my_text = line_edit.text()
        if len(set(my_text)) < 4 or is_valid_string(my_text) == False:
            self.login_button.setEnabled(False)

            line_edit.setStyleSheet("color: red;  background-color: white")
        else:
            line_edit.setStyleSheet("color: black;  background-color: white")
        if len(set(self.pass_text.text())) > 3 and len(set(self.login_text.text())) > 3:
            self.login_button.setEnabled(True)
        else:
            self.login_button.setEnabled(False)



    def setUpMainWindow(self):
        self.len_url = 0
        self.filename = datetime.datetime.now()
        """Создайте и расположите виджеты в главном окне."""
        self.header_label = QLabel("Urban parser")
        self.header_label.setFont(QFont("Arial", 18))
        self.header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Введите учётку:")
        question_label.setAlignment(Qt.AlignmentFlag.AlignBottom)

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
        self.main_v_box.addWidget(self.header_label)
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
        self.remember_me_checkBox = QCheckBox("Запомнить меня", self)
        if os.path.exists(self.credentials_path):
            self.remember_me_checkBox.setChecked(True)
            with open(self.credentials_path,'r') as json_data:
                credentials = json.load(json_data)
                json_user = credentials['username']
                json_pass = credentials['password']
                # print("json", json_user)
            self.login_text.setText(json_user)
            self.pass_text.setText(json_pass)


        self.main_v_box.addWidget(self.show_password_cb)
        self.main_v_box.addWidget(self.remember_me_checkBox)

        self.login_button = QPushButton("Войти")
        button_group.addButton(self.login_button)
        if len(self.login_text.text()) < 4:
            self.login_button.setEnabled(False)
        else:
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

        self.setLayout(self.main_v_box)

        # seach_action.triggered.connect(self.save_file)
        self.show_password_cb.toggled.connect(self.displayPasswordIfChecked)
        self.login_button.pressed.connect(self.start_auth_thread)
        # self.login_button.pressed.connect(self.checkAutorization)
        self.easy_button.clicked.connect(self.start_easy_thread)
        self.login_text.textEdited.connect(lambda: self.line_edit_rules(self.login_text))
        self.pass_text.textEdited.connect(lambda: self.line_edit_rules(self.pass_text))

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
        gc: Client = gspread.service_account("./icons/google_service_account.json")
        sh: Spreadsheet = gc.open_by_url(self.google_sheet_url)
        ws = sh.sheet1
        self.ws_tarif = sh.worksheet('tarifs')

        pass_base = BasePassParcer.verify_person(self,ws,"yulia")

        if self.pass_text.text() == pass_base:
            print("Verno")
        else:
            # print("Neverno")
            self.login_button.setEnabled(True)
            self.login_button.setText("Войти")

    def get_all_queries(self):
        self.all_queries, self.id_person = self.thread.get_all_queries()
        # return self.all_queries, self.id_person

    def openMainWithLogin(self):
        from main_window import MainWindow
        self.close()
        self.get_all_queries()
        self.w = MainWindow(self.all_queries, self.id_person)
        if self.remember_me_checkBox.isChecked():
            print(111)
        else:
            print(self.remember_me_checkBox.isChecked())
        self.save_credentials()
        self.w.show()

    def start_auth_thread(self):

        self.thread = ThreadClass(self.pass_text.text(), self.login_button, self.login_text, self.header_label, index=1)
        self.thread.any_signal.connect(self.update_progress_bar)
        self.thread.accept_signal.connect(self.openMainWithLogin)
        self.thread.start()
        # print(111)

    def start_easy_thread(self):
        self.thread = ThreadClass(self.pass_text.text(), self.login_button, self.login_text, self.header_label, index=2)
        self.thread.any_signal.connect(self.update_progress_bar)
        self.thread.accept_signal.connect(self.openMainWithLogin)
        self.thread.start()


    def update_progress_bar(self, value):
        self.prog_bar.setValue(value)

    def save_credentials(self): # Запомнить пользователя
        if self.remember_me_checkBox.isChecked():
            credentials = {
                "username": self.login_text.text(),
                "password": self.pass_text.text()
            }
            with open(self.credentials_path, "w") as file:
                json.dump(credentials, file)
        else:
            if os.path.exists(self.credentials_path):
                os.remove(self.credentials_path)

    def openMainEasy(self):
        # from add_pass_to_base import BasePassParcer
        from main_window import MainWindow

        self.close()
        self.w = MainWindow()
        self.w.show()

class ThreadClass(QThread):
    any_signal = pyqtSignal(int)
    accept_signal = pyqtSignal(int)

    def __init__(self, password, button, user_name,label, parent=None, index = 0):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True
        self.password = password
        self.button = button
        self.user_name = user_name.text()
        self.label = label

        self.google_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        sh: Spreadsheet = gc.open_by_url(self.google_sheet_url)
        self.ws = sh.sheet1

    def get_all_queries(self):
        return self.all_queries, self.id_person


    def easy_enter(self):
        from add_pass_to_base import BasePassParcer
        base_pass_parser = BasePassParcer()
        self.id_person, self.all_queries = base_pass_parser.verify_computer(self.ws)
        self.accept_signal.emit(100) #перейти в следующее окно

    def checkAutorization(self):
        from add_pass_to_base import BasePassParcer
        base_pass_parser = BasePassParcer()
        print(self.user_name)
        self.id_person, pass_base, self.all_queries = base_pass_parser.verify_person( self.ws, self.user_name)
        print("pass=", pass_base)
        cnt = 50
        self.any_signal.emit(cnt)

        if pass_base:
            cnt = 60
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
                self.label.setText("Неверный пароль")

        else:
            self.label.setText("Неверный логин")
            self.button.setText("Войти")
            self.button.setEnabled(True)

    def run(self):
        # print(self.index, 'index')

        self.button.setEnabled(False)
        self.button.setText("Ожидайте")
        self.label.setText("Загрузка...")
        #
        # from add_pass_to_base import BasePassParcer
        cnt = 10
        self.any_signal.emit(cnt)
        # pass_base = BasePassParcer.verify_person(self, self.ws, self.user_name)
        if self.index == 1:
            self.checkAutorization()

        elif self.index == 2:
            self.easy_enter()


    def stop(self):
        self.is_running = False
        self.terminate()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowAuth()
    sys.exit(app.exec())



