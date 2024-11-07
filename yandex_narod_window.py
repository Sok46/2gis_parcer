import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,
                             QHBoxLayout, QSpinBox, QFileDialog)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QTimer
from add_pass_to_base import BasePassParcer
from gspread import Client, Spreadsheet
import gspread
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


        self.logi = []
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
        # if 'где каждый делает карты точнее' in str(self.driver.page_source):
        else:
            self.auth_yandex()
            print(121231312)


        # sleep(10)
        # self.load_cookies(self.driver)
        #
        #
        self.timer.start()
        self.timer_2.start()

    def parse(self):
        filter_log.filter_log.logs_func(filter_log, self.driver, self.logi, self.excel_df, self.index_features)

    def update_counter(self):
        self.counter += 1
        self.sec_label.setText(str(self.counter))

    def yet_another_widgets(self):
        self.sec_label = QLabel('0', self)
        self.main_v_box.insertWidget(1, self.sec_label)

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

        # #Autorization
        # sleep(2)
        # ent_but = driver.find_element(By.XPATH,'/html/body/div/div[1]/div/div[2]/a/span')
        # self.actions.click(ent_but).perform()
        # sleep(1)
        # login_field = driver.find_element(By.XPATH,'//*[@id="passp-field-login"]')
        # sleep(1)
        # login_field.clear()
        # sleep(2)
        # login_field.send_keys("Doshirag2@yandex.ru")
        # login_field.send_keys(Keys.ENTER)
        #
        # sleep(3)
        # pass_input = driver.find_element(By.XPATH,'//*[@id="passp-field-passwd"]')
        # pass_input.clear()
        # sleep(2)
        # pass_input.send_keys("1124561luk")
        # sleep(2)
        # pass_input.send_keys(Keys.ENTER)
        # sleep(25)
    def save_auth(self):
        pickle.dump(self.driver.get_cookies(),open(f"yandex_cookies", "wb"))
        try:
            self.main_v_box.removeWidget(self.auth_butt)
            self.auth_butt.deleteLater()
            self.sec_label.setText("0")
        except:
            pass






    def load_cookies(self,driver):
        for cookie in pickle.load(open(f"yandex_cookies", "rb")):
            driver.add_cookie(cookie)
        sleep(2)
        driver.refresh()
        sleep(2)

    def connects(self):
        self.browser_button.clicked.connect(self.openBrowser)
        self.timer.timeout.connect(self.update_counter)
        self.timer_2.timeout.connect(self.parse)


        # # def logs_func(self, driver, logi, excel_df, index_features):
        #
        # logs_raw = driver.get_log("performance")
        # logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
        #
        # # print(logs, '\n stop logs \n')
        #
        # def log_filter(log_):
        #     return (
        #         # is an actual response
        #             log_["method"] == "Network.responseReceived"
        #             # and json
        #             and "json" in log_["params"]["response"]["mimeType"]
        #     )
        #
        # for log in filter(log_filter, logs):
        #
        #     try:
        #         request_id = log["params"]["requestId"]
        #         resp_url = log["params"]["response"]["url"]
        #         resp_qq = log["params"]["response"]
        #
        #         # print(f"Caught {resp_url}", '\n stop \n')
        #         # print('\n start driver \n ',driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}), '\n end driver \n')
        #         l = (driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}))
        #         logi.append(l)
        #     except:
        #         pass
        # bodyes = []
        # # matching_coordinates = []
        # ThreadMetaData = []
        #
        # features_list = []
        # stops = {
        #     "type": "FeatureCollection",
        #     "features": []
        # }
        #
        # # Перебираем все fetch/xhr
        # for i, body in enumerate(logi):
        #     try:
        #         data = body['body']
        #         # if i == 1:
        #         json_data = json.loads((data))
        #         # print("\n",json_data,"\n")
        #         # print(f'\n ', json_data["data"]['features'], '\n')
        #         # print(f'\n body{i}')
        #         bodyes.append(json_data["data"][-1])
        #         # for lst in json_data['data']:
        #         #     print(lst, "\n")
        #
        #     except:
        #         pass
        # geojson_data = {
        #     "type": "FeatureCollection",
        #     "features": []
        # }
        #
        # matching_prop = []
        # matching_coordinates = []
        # id_obj = []
        # name_obj = []
        # # print(bodyes)
        # for last_body_item in bodyes:
        #     try:
        #         # if last_body_item['data']['features']:
        #         # print(last_body_item['data'])
        #         many_features = last_body_item['data']['features']
        #         for feature in many_features:
        #             # feature = features.split("RenderedGeometry")
        #             properties = feature['properties']
        #             prop = properties["hintContent"]
        #             g_obj = properties['geoObject']['geometry']
        #             id = properties['geoObject']['id']
        #             if "(" in prop:
        #                 name = prop.split("(")[0]
        #                 prop = prop.split("(")[1]
        #
        #                 # prop = excel_df.loc[excel_df['prop'] == prop, 'new_name'].values
        #             else:
        #                 name = "-"
        #             # Пример использования объединенных данных
        #             for index, row in excel_df.iterrows():
        #                 prop_xlsx = row['prop']
        #                 new_xlsx = row['new_name']
        #                 if prop_xlsx in prop:
        #                     prop = prop.replace(prop, new_xlsx)
        #             # print("prop:",prop_match)
        #
        #             id_obj.append(id)
        #             name_obj.append(name)
        #             matching_prop.append(prop)
        #             matching_coordinates.append(g_obj)
        #
        #             # print("\n", "g_obj:",g_obj, "\n")
        #
        #         # print("\n", route_features, "\n")
        #     except:
        #         pass
        # # print()
        #
        # if len(id_obj) != 0:
        #     # print("id_obj",id_obj)
        #     #     index_features.append(0)
        #     # else:
        #     index_features.append(set(id_obj))
        #
        # features = []
        # for i in range(len(matching_coordinates)):
        #     feature = {
        #         "type": "Feature",
        #         # "properties:"
        #         "id": id_obj[i],
        #         "name": name_obj[i],
        #         "category": matching_prop[i],
        #
        #         "geometry": matching_coordinates[i]
        #     }
        #     # unique_feature =  dict.fromkeys(feature).keys()
        #     features.append(feature)
        #     # index_features.append(len(features))
        # # print("features:",features)
        # # clear_features = list(set(map(str, features)))
        #
        # # print("clear:", features)
        #
        # geojson_data = {
        #     "type": "FeatureCollection",
        #     # "crs": {
        #     #     "type": "name",
        #     #     "properties": {
        #     #         "name": "urn:ogc:def:crs:EPSG::3395"
        #     #     }
        #     # },
        #     "features": features
        # }
        # # geojson_str = json.dumps(geojson_data)
        # # print(geojson_data)
        # return geojson_data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NarodWidget()
    sys.exit(app.exec())
