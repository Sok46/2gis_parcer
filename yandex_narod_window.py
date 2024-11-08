import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,
                             QHBoxLayout, QSpinBox, QFileDialog)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from add_pass_to_base import BasePassParcer
from gspread import Client, Spreadsheet
import gspread
import geopandas as gpd
from time import sleep
import pickle
import json
from base_widget import MyWidget
import filter_log
import os.path

from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import pandas as pd


from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import gspread
from gspread import Client, Spreadsheet
from add_pass_to_base import BasePassParcer


class NarodWidget(MyWidget):
    def __init__(self, count_queries=50, id_person=10):
        super().__init__()
        self.counter = 0
        #
        self.count_queries = int(count_queries)
        self.id_person = id_person
        self.header_label.setText(f"У вас {self.count_queries} запросов")
        # Create and setup timer
        self.timer = QTimer()
        self.timer.setInterval(1000)

        self.timer_2 = QTimer()
        self.timer_2.setInterval(10000)

        self.yet_another_widgets()
        self.connects()



        self.index_features = []
        self.excel_df = pd.read_excel('./etc/yand_categoty.xlsx')


    def openBrowser(self):
        # capabilities = DesiredCapabilities.CHROME
        options = webdriver.ChromeOptions()
        options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL"}
        )
        self.driver = webdriver.Chrome(options=options)
        url = 'https://n.maps.yandex.ru/#!/?z=16&ll=91.428643%2C53.722016&l=nk%23sat'
        self.save_path_textedit.setReadOnly(True)

        self.driver.get(url)
        # self.parce_button.setEnabled(True)
        self.browser_button.setEnabled(False)
        self.actions = ActionChains(self.driver)
        sleep(4)
        if self.check_auth_file():
            print('check_auth_file')
            self.load_cookies(self.driver)

            self.start_timer()
        # if 'где каждый делает карты точнее' in str(self.driver.page_source):
        else:
            self.auth_yandex()


        # sleep(10)
        # self.load_cookies(self.driver)
        #
        #


    def parse(self):
        self.logi = []

        logs_fast = filter_log.filter_log.logs_func(filter_log, self.driver, self.logi, self.excel_df, self.index_features)
        geojson_str = json.dumps(logs_fast)
        # print('logs_return compl')
        # # Игнор ошибок
        # original_stder = sys.stderr
        # # sys.stderr = NullWritter()
        # gdf_logs_return = gpd.read_file(geojson_str)
        # sys.stderr = original_stder
        # print('gdf_logs_return compl')
        # num_logs_return = gdf_logs_return.shape[0]
        # print('num_logs_return compl')
        file_path = rf'{layers_path}\builds_saves_{max_ekr_vertikal}_{ekrans}.gpkg'
        gdf.to_file(file_path,layer='имя_вашего_слоя', driver="GPKG")

    def update_counter(self):
        self.counter += 1
        self.sec_label.setText(str(self.counter))

    def yet_another_widgets(self):
        self.sec_label = QLabel('0', self)
        self.main_v_box.insertWidget(1, self.sec_label)
    def start_timer(self):
        self.timer.start()
        self.timer_2.start()

    def auth_yandex(self):
        self.sec_label.setText("Авторизуйтесь!")
        self.auth_butt = QPushButton("Я авторизовался, запомни меня")
        self.main_v_box.insertWidget(2,self.auth_butt)

        self.auth_butt.clicked.connect(self.save_auth)
    def check_auth_file(self):
        if os.path.exists("yandex_cookies"):
            return True
        else:
            return False

    def save_auth(self):

        try:
            self.main_v_box.removeWidget(self.auth_butt)
            self.auth_butt.deleteLater()
            self.sec_label.setText("0")
        except:
            pass
        pickle.dump(self.driver.get_cookies(), open(f"yandex_cookies", "wb"))
        self.start_timer()

    def load_cookies(self,driver):
        for cookie in pickle.load(open(f"yandex_cookies", "rb")):
            driver.add_cookie(cookie)
        sleep(2)
        driver.refresh()
        sleep(2)

    def start_thread(self):
        self.thread = ThreadClass(self.driver, self.logi, self.excel_df, self.index_features, index=1)
        # self.thread.any_signal.connect(self.update_progress_bar)
        # self.thread.accept_signal.connect(self.openMainWithLogin)
        self.thread.start()

    def connects(self):
        self.browser_button.clicked.connect(self.openBrowser)
        self.timer.timeout.connect(self.update_counter)
        self.timer_2.timeout.connect(self.start_thread)

class ThreadClass(QThread):
    any_signal = pyqtSignal(int)
    accept_signal = pyqtSignal(int)

    def __init__(self, driver, logi, excel_df, index_features, parent=None, index = 0):
        super(ThreadClass, self).__init__(parent)

        self.index = index
        self.is_running = True
        self.driver = driver
        self.logi = logi
        self.excel_df = excel_df
        self.index_features = index_features

        self.google_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        sh: Spreadsheet = gc.open_by_url(self.google_sheet_url)
        self.ws = sh.sheet1

    def parse(self):
        filter_log.filter_log.logs_func(filter_log, self.driver, self.logi, self.excel_df, self.index_features)



    def run(self):
        # print(self.index, 'index')


        if self.index == 1:
            self.parse()

        # elif self.index == 2:
        #     self.easy_enter()


    def stop(self):
        self.is_running = False
        self.terminate()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NarodWidget()
    sys.exit(app.exec())
