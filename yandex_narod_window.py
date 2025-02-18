import sys
from PyQt6.QtWidgets import (QApplication,  QLabel, QPushButton)

from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

import geopandas as gpd
from time import sleep
import pickle
import json
from base_widget import MyWidget
import filter_log
import os.path
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import pandas as pd
from query_setter import QuerySetter
import gspread
from gspread import Client, Spreadsheet
import fiona

class NarodWidget(MyWidget):
    def __init__(self, count_queries=50, id_person=10, price_query = 20):
        super().__init__()
        self.counter = 0
        self.num_file = 0
        #
        self.priceQuery = price_query
        self.count_queries = int(count_queries)
        self.id_person = id_person
        self.header_label.setText(f'У вас {self.count_queries} <img src={self.coinIcon_path} width="30" height="30" style="vertical-align: top;">')
        self.browser_button.setText(f"Начать парсинг   ({self.priceQuery})")
        # Create and setup timer
        self.timer = QTimer()
        self.timer.setInterval(1000)

        self.timer_2 = QTimer()
        self.timer_2.setInterval(15000)
        # file_path = self.save_path_textedit.te

        self.cityname_textedit.setEnabled(False)
        self.yet_another_widgets()
        self.connects()
        self.logi = []



        self.index_features = []
        self.excel_df = pd.read_excel('./icons/yand_categoty.xlsx')


    def stop_parsing(self):
        self.timer.stop()
        self.sec_label.setText('Таймер парсинга: 0')
        self.driver.close()
        self.browser_button.setEnabled(True)
        self.stop_button.hide()
        self.counter = 0

        # self.main_v_box.removeWidget(self.stop_button)




    def openBrowser(self):
        self.stop_button.show()


        # capabilities = DesiredCapabilities.CHROME
        options = webdriver.ChromeOptions()
        options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL"}
        )
        self.driver = webdriver.Chrome(options=options)
        lat, long = self.cityname_textedit.text().strip().split(',')

        url = f'https://n.maps.yandex.ru/#!/?z=16&ll={long}%2C{lat}&l=nk%23sat'
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


    def update_counter(self):
        self.counter += 1
        self.sec_label.setText(f'Таймер парсинга:{self.counter}')
        if self.counter % 15 == 0:
            check_query = QuerySetter().check_query(self.count_queries, self.priceQuery, self.header_label)
            if check_query:
                self.start_thread()
                self.count_queries = QuerySetter().set_query(self.count_queries, self.my_base, self.header_label,
                                                             self.priceQuery, self.ws, self.id_person, self.sh)
            else:
                self.stop_parsing()

    def yet_another_widgets(self):

        self.sec_label = QLabel(f'Таймер парсинга: 0', self)
        self.main_v_box.insertWidget(1, self.sec_label)
        self.cityname_label.setText("Координаты старта")
        self.cityname_textedit.setPlaceholderText("55.751731, 37.618867")
        self.stop_button = QPushButton("СТОП")
        self.stop_button.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.main_v_box.insertWidget(1, self.stop_button)  # КНОПКА СТОП
        self.stop_button.hide()

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
            self.sec_label.setText('Таймер парсинга: 0')
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
        # check_query = QuerySetter().check_query(self.count_queries, 50, self.header_label)
        # if check_query:
        self.num_file +=1
        self.thread = ThreadClass(self.driver, self.logi, self.excel_df, self.index_features, self.num_file, self.save_path_textedit.text(),index=1)
        # self.thread.any_signal.connect(self.update_progress_bar)
        # self.thread.accept_signal.connect(self.openMainWithLogin)
        self.thread.start()


    def connects(self):
        self.browser_button.clicked.connect(self.openBrowser)
        self.timer.timeout.connect(self.update_counter)
        self.stop_button.clicked.connect(self.stop_parsing)

        # self.timer_2.timeout.connect(self.start_thread)

class ThreadClass(QThread):
    any_signal = pyqtSignal(int)
    accept_signal = pyqtSignal(int)

    def __init__(self, driver, logi, excel_df, index_features,num_file,file_path, parent=None, index = 0):
        super(ThreadClass, self).__init__(parent)
        self.num_file = num_file
        self.filepath = file_path

        self.index = index
        self.is_running = True
        self.driver = driver
        self.logi = logi
        self.excel_df = excel_df
        self.index_features = index_features

        self.google_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        gc: Client = gspread.service_account("./icons/google_service_account.json")
        sh: Spreadsheet = gc.open_by_url(self.google_sheet_url)
        self.ws = sh.sheet1

    def parse(self):
        narod_logs = filter_log.filter_log.logs_func(filter_log, self.driver, self.logi, self.excel_df, self.index_features)
        geojson_str = json.dumps(narod_logs)
        print('geojson_str')
        gdf_logs_return = gpd.read_file(geojson_str)

        file_path = rf'{self.filepath}\narod_map.gpkg'

        gdf_logs_return.to_file(file_path,layer=f"Геометрия Яндекса", driver="GPKG")

        self.logi.clear()
        self.index_features.clear()



    def run(self):

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
