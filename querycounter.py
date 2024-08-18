
import gspread
from gspread import Cell, Client, Spreadsheet, Worksheet
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,
                             QCheckBox, QFileDialog,QHBoxLayout,QProgressBar)
from PyQt6.QtGui import QFont, QPixmap, QAction, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import  datetime
import socket
import os
from  authorization_window import WindowAuth
class QueryCounter(WindowAuth):
    def __init__(self):
        self.googe_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        # self.thread = ThreadClass('', None, None, self.header_label, index=2)

        self.all_query  = self.get_all_queries()
    def spend_query(self, ws: Worksheet):
        self.all_query -= 1
        print(self.all_query)

class ThreadClass(QThread):
    any_signal = pyqtSignal(int)
    accept_signal = pyqtSignal(int)

    def __init__(self, user_name,label, parent=None, index = None):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True
        self.user_name = user_name.text()
        self.label = label

        self.google_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        sh: Spreadsheet = gc.open_by_url(self.google_sheet_url)
        self.ws = sh.sheet1

    def get_all_queries(self):
        from add_pass_to_base import BasePassParcer
        id_person, self.all_queries = BasePassParcer.verify_computer(self, self.ws)
        self.label.setText("Неверный логин")
        print(self.all_queries)

    def run(self):
        print(self.index, 'index')
        self.label.setText("Загрузка...")
        from add_pass_to_base import BasePassParcer
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


    def stop(self):
        self.is_running = False
        print('stop thread...', self.index)
        self.terminate()






if __name__ == '__main__':
    counter = QueryCounter()
    counter.spend_query()
