import sys
from PyQt6.QtWidgets import (QApplication,  QLabel, QPushButton,QLineEdit)
import datetime
from PyQt6.QtCore import Qt
import json
from base_widget import MyWidget
import filter_log_geochecks
import pandas as pd
from query_setter import QuerySetter
import gspread
from gspread import Client, Spreadsheet
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class WindowYandexRoute(MyWidget):
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

        self.yet_another_widgets()
        self.connects()
        self.logi = []
        self.index_features = []
        self.excel_df = pd.read_excel('./icons/yand_categoty.xlsx')

    def parce(self):
        check_query = QuerySetter().check_query(self.count_queries, 30, self.header_label)
        if check_query:
            url = 'https://yandex.ru/maps/11310/minusinsk/?ll=91.696668%2C53.700875&z=12.63'

            # make chrome log requests
            capabilities = DesiredCapabilities.CHROME
            options = webdriver.ChromeOptions()
            options.set_capability(
                "goog:loggingPrefs", {"performance": "ALL", 'browser': 'ALL'}
            )
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            actions = ActionChains(driver)
            time.sleep(3)
            try:
                input_query = driver.find_element(By.XPATH, '//input[@placeholder="Поиск и выбор мест"]')
                input_query.click()
                time.sleep(1)
                input_query.send_keys(Keys.CONTROL + 'a')
                time.sleep(1)
                input_query.send_keys(Keys.BACKSPACE)
                time.sleep(1)
                actions.send_keys(self.cityname_textedit.text()).perform()
                time.sleep(1)
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(1)
            except Exception as e:
                print(e)
                print("Вылетела капча")
                return

            # df = pd.read_excel(r'C:\Users\sergey.biryukov\Downloads\Shlak\центроиды кем.xlsx', sheet_name='фффф')
            iter_routes = self.routes_textedit.text().split(",")
            print(iter_routes)
            for index, row in enumerate(iter_routes):
                if len(row) < 7:
                    row = "Маршрут " + row
                routes_feats = []
                index_feats = []

                input_query.click()
                time.sleep(1)
                input_query.send_keys(Keys.CONTROL + 'a')
                time.sleep(1)
                input_query.send_keys(Keys.BACKSPACE)
                time.sleep(1)
                actions.send_keys(row).perform()
                time.sleep(1)
                actions.send_keys(Keys.ENTER).perform()

                time.sleep(6)

                logs_raw = driver.get_log("performance")
                logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

                def log_filter(log_):
                    return (
                        # is an actual response
                            log_["method"] == "Network.responseReceived"
                            # and json
                            and "json" in log_["params"]["response"]["mimeType"]
                    )

                routes_geoms = []
                stops_geoms = []

                for log in filter(log_filter, logs):
                    try:
                        request_id = log["params"]["requestId"]
                        resp_url = log["params"]["response"]["url"]
                        resp_qq = log["params"]["response"]

                        # print(f"Caught {resp_url}", '\n stop \n')
                        # print('\n start driver \n ',driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}), '\n end driver \n')
                        l = (driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}))
                        # print(l)
                        routes_feats.append(l)
                    except:
                        pass

                    stop_coors = []
                    stop_names = []

                    matching_coordinates = []
                    types = []
                    numbers = []

                    ThreadMetaData = []

                    # Подготовка списка для хранения подходящих координат
                    matching_prop = []
                    matching_discr = []

                    # Перебираем все fetch/xhr
                    for i, body in enumerate(routes_feats):
                        # print(1, body)
                        try:
                            data = body['body']
                            # print(data)
                            # if i == 1:
                            json_data_main = json.loads((data))
                            data = json_data_main['data']['features']
                            # print(data)
                            for d in data:

                                number = d['properties']['ThreadMetaData']['name']
                                numbers.append(number)

                                type_route = d['properties']['ThreadMetaData']['type']
                                types.append(type_route)
                                names = []
                                print(number, type_route)
                                for k, feature in enumerate(d['features']):
                                    # stop_coor = feature["coordinates"]
                                    # print(stop_coor)
                                    # print(feature)
                                    name = feature.get("name")
                                    # print(name, k)
                                    names.append(name)
                                    if "points" in feature:
                                        points = feature["points"]
                                        # print(points)
                                        matching_coordinates.append(points)
                                        # name = feature["id"]
                                    if "coordinates" in feature:
                                        stop_coor = feature["coordinates"]
                                        stop_coors.append(stop_coor)
                                        stop_names.append(feature["name"])
                                print(names)

                                for j, coordinates in enumerate(matching_coordinates):
                                    route = {
                                        "type": "Feature",
                                        "geometry": {
                                            "type": "LineString",
                                            "coordinates": coordinates
                                        },
                                        "properties": {
                                            "out": names[0],
                                            'in': names[-1],
                                            'out_in': str(names[0]) + '-' + str(names[-1]),
                                            "type": types[0],
                                            "route": numbers[0],
                                        }
                                    }
                                    routes_geoms.append(route)
                                for i, coordinates in enumerate(stop_coors):
                                    stops_data = {
                                        "type": "Feature",
                                        "geometry": {
                                            "type": "Point",
                                            "coordinates": coordinates
                                        },
                                        "properties": {
                                            "out": stop_names[i],
                                            #     'in': names[-1],
                                            #     'out_in': str(names[0]) + '-' + str(names[-1])
                                        }
                                    }

                                    # if len(route_data) > 0:
                                    stops_geoms.append(stops_data)
                        except:
                            pass
                try:
                    # print(names)
                    geojson_data = {
                        "type": "FeatureCollection",
                        "features": routes_geoms
                    }

                    stops_data = {
                        "type": "FeatureCollection",
                        "features": stops_geoms
                    }
                    # print(types)
                    output_geojson_path = rf'{self.save_path_textedit.text()}\{types[0]}_{numbers[0]}'
                    print(output_geojson_path)
                    output_stops_geojson_path = rf'{self.save_path_textedit.text()}\{types[0]}_{numbers[0]}'

                    with open(output_geojson_path + ".geojson", 'w', encoding='utf-8') as output_geojson_file:
                        json.dump(geojson_data, output_geojson_file, indent=2, ensure_ascii=False)

                    with open(output_stops_geojson_path + '_stops' + ".geojson", 'w',
                              encoding='utf-8') as output_geojson_file:
                        json.dump(stops_data, output_geojson_file, indent=2, ensure_ascii=False)

                except:
                    pass

                self.count_queries = QuerySetter().set_query(self.count_queries, self.my_base, self.header_label,
                                                             30, self.ws, self.id_person, self.sh)

                print("route save")

    def yet_another_widgets(self):
        routes_label = QLabel("Номера маршрутов для скачивания")
        routes_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_v_box.insertWidget(5, routes_label)
        self.routes_textedit = QLineEdit()
        self.routes_textedit.setPlaceholderText("Пример: 8,5, троллейбус 2, трам 125")
        self.main_v_box.insertWidget(6, self.routes_textedit)

    def connects(self):
        self.browser_button.clicked.connect(self.parce)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowYandexRoute()
    sys.exit(app.exec())
