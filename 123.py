import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,QHBoxLayout,QFileDialog,
                             QComboBox,QCheckBox,QGridLayout,QGroupBox,QScrollArea, QProgressBar)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QCoreApplication
import os
import gspread
from gspread import Client, Spreadsheet
from add_pass_to_base import BasePassParcer
import pandas as pd
import requests
from urllib.parse import urlencode
import yadisk
import numpy as np
import bisect

from query_setter import QuerySetter
from base_widget import MyWidget


class WindowGisJkh(MyWidget):
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

    def change_directory(self):
        if len(self.save_path_textedit.text()) > 3:
            self.scroll.setEnabled(True)
            self.confirm_button.setEnabled(True)
            # self.browser_button.setEnabled(True)
            self.cityname_textedit.setEnabled(True)
            if len(self.cityname_textedit.text()) > 3: #Если город введен вручную
                self.stage = 1
                self.browser_button.setEnabled(True)
                print(33333)
            # elif self.checked_cities and len(self.checked_cities) > 0: #Если выбран
            #     self.stage = 2
            #     self.browser_button.setEnabled(True)
            else:
                self.browser_button.setEnabled(False)

        else:
            self.stage = 0
            self.scroll.setEnabled(False)
            self.confirm_button.setEnabled(False)
            self.browser_button.setEnabled(False)
            self.cityname_textedit.setEnabled(False)
    def enabled_checkbox(self):
        if self.checked_cities and len(self.checked_cities) > 0:  # Если выбран
            self.stage = 2
            self.browser_button.setEnabled(True)
        else:
            self.browser_button.setEnabled(False)

    def set_regions(self): #Заполняем комбобокс нашими регионами

        regions = []
        for item in self.y.listdir(self.gis_folder):
            file = f"path: {item['path']}"
            region = file.split('Сведения по ОЖФ ')[1].split(' на ')[0]
            regions.append(region)
        self.region_combobox.addItems(sorted(list(set(regions))))
        print(self.region_combobox.currentText())

    def get_selected_regions(self):
        self.sheets_urls = []
        for item in self.y.listdir(self.gis_folder):
            # print(f"{item['path']}")

            if self.region_combobox.currentText() in f"{item['path']}":
                print(f"{item['path']}")
                sheet_url = item['public_url']
                self.sheets_urls.append(sheet_url)
    def get_cities(self):
        self.get_selected_regions()

        for url in self.sheets_urls:
            print(url)
            final_url = self.base_url + urlencode(dict(public_key=url))
            response = requests.get(final_url)
            download_url = response.json()['href']
            df = pd.read_csv(download_url, sep='|')
            split_values = df['Адрес ОЖФ'].str.split(',', expand=True)
            # unique_values = df['Адрес ОЖФ'].str.split(',', expand=True).iloc[:, ::-1]

            # Функция для нахождения нужного элемента после "р-н" или "Респ"
            def find_element_after(values):
                idx_city = values[values.str.contains(r'\bг\. ', na=False)].index

                if len(idx_city) > 0:
                    # Если найден 'г. ', возвращаем элемент, содержащий 'г. '
                    return values[idx_city[0]]
                else:
                    # Пытаемся найти индекс элемента, содержащего 'р-н'
                    idx_rn = values[values.str.contains(r'\bр-н\b', na=False)].index

                    if len(idx_rn) > 0:
                        # Если найден 'р-н', возвращаем элемент после него
                        idx = idx_rn[0] + 1
                    else:
                        # Если не найден 'р-н', ищем 'Респ'
                        idx_resp = values[values.str.contains(self.region_combobox.currentText(), na=False)].index
                        if len(idx_resp) > 0:
                            # Если найден 'Респ', возвращаем элемент после него
                            idx = idx_resp[0] + 1
                        else:
                            # Если не найдено ни 'р-н', ни 'Респ', возвращаем NaN
                            return np.nan


                # Проверяем, есть ли элемент после найденного индекса
                if idx < len(values):
                    return values[idx]
                else:
                    return np.nan

            print('find_element_after')
            # Применяем функцию к каждой строке DataFrame
            unique_cities = split_values.apply(find_element_after, axis=1).unique()
            print(unique_cities)


            for i, city in enumerate(unique_cities):
                print(city)
                type_city = city.split('. ')[0]

                key = type_city  # первая часть
                # value = city.split('. ')[1]  # вторая часть
                # Если ключ уже существует в словаре
                if key in self.cities_dict:
                    #если город уже есть в словаре (при 2х и более csv)
                    if city in self.cities_dict[key]:
                        continue
                    else:
                        # Вставляем новое значение в список в алфавитном порядке
                        bisect.insort(self.cities_dict[key], city)
                else:
                    # Создаем новый ключ со списком и сразу добавляем значение
                    self.cities_dict[key] = [city]

        print(self.cities_dict)

    def select_all_checkboxes(self):
        if self.all_checkboxes.isChecked():
            status = True
        else:
            status = False
        # Перебираем все QCheckBox и устанавливаем их состояние в "выбрано"
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(status)

    def set_cities(self): #Вставляет полученные города из get cities в группу
        self.cities_dict = self.thread.cities_dict
        self.clearLayout(self.load_city_layout)
        # self.get_cities()



        city_layout = QVBoxLayout()
        city_layout.addWidget(self.download_city_butt)
        city_layout.addWidget(self.all_checkboxes)

        for header in  self.cities_dict.keys():
            group = QGroupBox(header) #Cоздаём группу чекбоксов
            myFont = QFont()
            myFont.setBold(True)
            group.setFont(myFont)
            layout = QVBoxLayout()

            for city in self.cities_dict[header]:

                checkbox = QCheckBox(city) #Добавляем чекбоксы в группу
                myFont.setBold(False)
                checkbox.setFont(myFont)
                layout.addWidget(checkbox)
                checkbox.checkStateChanged.connect(self.on_checkbox_state_changed)
            group.setLayout(layout)

            city_layout.addWidget(group)

        self.city_group.setLayout(city_layout)

        self.scroll.setFixedHeight(300)
        self.scroll.setWidget(self.city_group)

        # self.download_city_butt.clicked.connect(self.download_cities())
        # self.scroll.setLayout(white_layout)

        # self.main_v_box.addWidget(self.scroll)

            # self.city_combobox.addItems(unique_cities)
    def download_cities(self):

        cities = []
        print(cities)
        for header in  self.cities_dict.keys():
            for city in self.cities_dict[header]:
                cities.append(city)
        check_query = QuerySetter().check_query(self.count_queries, len(cities), self.header_label)
        if check_query:
            df = pd.DataFrame(cities, columns=["города"])
            df.to_csv(self.save_path_textedit.text() + '/cities.csv', index=False, encoding='cp1251')
            self.count_queries = QuerySetter().set_query(self.count_queries, self.my_base, self.header_label, len(cities), self.ws, self.id_person, self.sh)
        # self.count_queries -= len(cities)
        # print(len(self.cities_dict.keys()))
        # self.my_base.set_queries(self.ws, int(self.id_person), self.sh, int(self.count_queries))
        # self.header_label.setText(f"У вас {self.count_queries} запросов")




    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def on_checkbox_state_changed(self, state):
        # Получаем все тексты активированных чекбоксов
        selected_cities = []
        for group in self.findChildren(QGroupBox):
            for checkbox in group.findChildren(QCheckBox):
                if checkbox.isChecked():
                    selected_cities.append(checkbox.text())
        self.checked_cities = set(selected_cities)
        self.enabled_checkbox()

    def save_file(self):
        f_dialog = QFileDialog().getExistingDirectory()
        # f_dialog = QFileDialog().getSaveFileName(self, "Save File", "парсинг 2гис", "csv Files (*.csv)")
        path = f_dialog
        self.save_path_textedit.setText(path)

    def parce(self):
        # print(self.cityname_textedit.text())
        folder = self.save_path_textedit.text()
        if not os.path.exists(folder + '\export'):
            os.makedirs(folder + '\export')
        self.get_selected_regions()
        for url in self.sheets_urls:
            print(url)
            final_url = self.base_url + urlencode(dict(public_key=url))
            response = requests.get(final_url)
            download_url = response.json()['href']
            df = pd.read_csv(download_url, sep='|')

            # Удаление индекса из начала строки в колонке "address"
            # df['Адрес ОЖФ'] = df['Адрес ОЖФ'].str.slice(8)

            df.loc[df['Адрес ОЖФ'].str.contains('^\d'), 'Адрес ОЖФ'] = df['Адрес ОЖФ'].str.slice(8)
            # print(df['Адрес ОЖФ'] )
            # Город, по которому будет выполняться фильтрация
            print("Проверка cityname_textedit")
            # if self.cityname_textedit and len(self.cityname_textedit.text()) > 2:
            if self.checked_cities is None:
                print(self.cityname_textedit.text())
                if ',' in self.cityname_textedit.text():
                    city_filter = f" {self.cityname_textedit.text()}".split(',')
                else:
                    city_filter = [f" {self.cityname_textedit.text()}"]

            else:
                print("cityname_textedit не введён")
                city_filter = self.checked_cities

            for city in city_filter:
                # Фильтрация данных по указанному городу, используя метод str.contains
                filtered_df = df[df['Адрес ОЖФ'].str.contains(city, na=False)]

                # Группировка и агрегация
                result = filtered_df.groupby('Адрес ОЖФ').agg(
                    # address =
                    total=('Адрес ОЖФ', 'count'),
                    total_living=('Тип помещения (блока)', lambda x: (x == 'Жилое').sum()),
                    total_non_living=('Тип помещения (блока)', lambda x: (x == 'Нежилое').sum()),
                    total_living_area=('Жилая площадь в доме', 'max'),
                    total_area=('Общая площадь дома', 'max'),
                    type=('Тип дома', 'first'),
                    status=('Состояние', 'first'),
                    state_host=(
                        'Дом находится в собственности субъекта Российской Федерации и в полном объеме используется в качестве общежития',
                        'first'),
                    substate_host=(
                        'Дом находится в муниципальной собственности и в полном объеме используется в качестве общежития',
                        'first'),
                    method=('Способ управления', 'first')
                ).reset_index()

                # if len(os.listdir(folder+'\export')) == 0:
                if f'ГИС_ЖКХ_{city}.csv' not in os.listdir(folder + '\export'):
                    header = True

                else:
                    header = False

                result.to_csv(rf'{folder}\export\ГИС_ЖКХ_{city}.csv', sep=';', encoding='cp1251', header=header,
                              mode='a', index=False)

    def yet_another_widgets(self):

        self.cityname_label.deleteLater()
        self.cityname_textedit.deleteLater()
        self.browser_button.deleteLater()
        self.stage = 0  # включение кнопок по ходу выполнения программы
        self.checked_cities = None
        tkn = "y0_AgAAAAAGvkyVAAyD3AAAAAESV2AkAABx7BX4XRNEv7zh0HWaFEzZX1T2nA"
        self.y = yadisk.YaDisk(token=tkn)
        self.gis_folder = "/ГИС ЖКХ/Сведения_об_объектах_жилищного_фонда_на_15-09-2024"  # Путь к папке на Яндексе
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'

        self.add_cities_button = QPushButton("Подгрузить Населённые пункты")

        question_label = QLabel("Выберете действие")
        question_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        button_group = QButtonGroup(self)
        # button_group.buttonClicked.connect(
        #     self.checkboxClicked)

        self.confirm_button = QPushButton("Завершить программу")
        self.confirm_button.setEnabled(False)
        # self.confirm_button.clicked.connect(self.stopDriver)
        # self.confirm_button.clicked.connect(self.close)

        # self.back_button = QPushButton("Назад")
        # self.back_button.setEnabled(True)

        # self.main_v_box = QVBoxLayout()
        self.main_v_box.insertWidget(0,self.header_label)
        # self.main_v_box.addWidget(question_label)

        self.main_h_box = QHBoxLayout()
        self.back_h_box = QHBoxLayout()

        # self.save_path_textedit = QLineEdit()
        # self.save_path_textedit.setClearButtonEnabled(True)
        # seach_action = self.save_path_textedit.addAction(QIcon('icons/folder_icon.png'),
        #                                                  QLineEdit.ActionPosition.LeadingPosition)

        # self.save_path_textedit.setPlaceholderText('Укажите путь для выходных csv ...')
        # self.main_v_box.addWidget(self.save_path_textedit)

        region_label = QLabel("Выберете регион")
        region_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_v_box.insertWidget(3,region_label)
        self.region_combobox = QComboBox()
        self.set_regions()
        self.main_v_box.insertWidget(4,self.region_combobox)

        self.city_group = QGroupBox("Населённые пункты")
        self.load_city_layout = QVBoxLayout()

        add_cities_button = QPushButton("Подгрузить Населённые пункты")
        self.prog_bar = QProgressBar()

        self.scroll = QScrollArea()

        # self.scroll.setWidget(add_cities_button)
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumSize(100,100)
        # self.scroll.baseSize()

        self.load_city_layout.addWidget(add_cities_button)
        # self.load_city_layout.addWidget(self.prog_bar)
        cityname_label = QLabel("Либо введите название населённого пункта самостоятельно")
        cityname_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        # self.main_v_box.addWidget(cityname_label)
        self.cityname_textedit = QLineEdit()
        self.cityname_textedit.setPlaceholderText("Например: г. Махачкала")
        # self.main_v_box.addWidget(self.cityname_textedit)

        self.load_city_layout.addWidget(cityname_label)
        self.load_city_layout.addWidget(self.cityname_textedit)
        # self.city_layout.addWidget(self.city_group)
        self.scroll.setLayout(self.load_city_layout)

        self.main_v_box.insertWidget(5,self.scroll)
        self.main_v_box.insertWidget(6,self.prog_bar)
        # self.main_v_box.setEnabled(False)

        self.download_city_butt = QPushButton("Выгрузить названия")
        self.all_checkboxes = QCheckBox("Выбрать все")

        self.browser_button = QPushButton("Получить дома")
        self.browser_button.setEnabled(True)
        self.main_v_box.insertWidget(7,self.browser_button)
        # self.main_v_box.insertWidget(self.back_button)

        self.change_directory()
        self.setLayout(self.main_v_box)

        # seach_action.triggered.connect(self.save_file)
        # self.back_button.clicked.connect(self.open_main)
        # self.browser_button.clicked.connect(self.parce)
        self.browser_button.clicked.connect(self.start_parce_thread)

        add_cities_button.clicked.connect(self.start_city_thread)
        # add_cities_button.clicked.connect(self.set_cities)
        self.download_city_butt.clicked.connect(self.download_cities)
        self.all_checkboxes.checkStateChanged.connect(self.select_all_checkboxes)

        # Сигналы для отображения кнопок
        # self.browser_button.clicked.connect(self.change_directory)
        self.cityname_textedit.textChanged.connect(self.change_directory)
        self.save_path_textedit.textChanged.connect(self.change_directory)

    def connects(self):
        self.browser_button.clicked.connect(self.parce)
        # seach_action.triggered.connect(self.save_file)
        # self.back_button.clicked.connect(self.open_main)
        # self.browser_button.clicked.connect(self.parce)
        self.browser_button.clicked.connect(self.start_parce_thread)

        self.add_cities_button.clicked.connect(self.start_city_thread)
        # add_cities_button.clicked.connect(self.set_cities)
        self.download_city_butt.clicked.connect(self.download_cities)
        self.all_checkboxes.checkStateChanged.connect(self.select_all_checkboxes)

        # Сигналы для отображения кнопок
        # self.browser_button.clicked.connect(self.change_directory)
        self.cityname_textedit.textChanged.connect(self.change_directory)
        self.save_path_textedit.textChanged.connect(self.change_directory)

    def start_city_thread(self):
        self.get_selected_regions()
        self.indx = 1
        self.thread = ThreadClass(self.sheets_urls, self.base_url, self.region_combobox,self.header_label, index=self.indx)
        self.thread.any_signal.connect(self.update_progress_bar)
        self.thread.start()
    def start_parce_thread(self):
        check_query = QuerySetter().check_query(self.count_queries, 200, self.header_label)
        if check_query:
            self.get_selected_regions()
            self.indx = 2
            if self.checked_cities is None:
                text_cities = self.cityname_textedit.text()
            else:
                text_cities = None

            self.thread = ThreadClass(self.sheets_urls, self.base_url, self.region_combobox,self.header_label, index=self.indx, folder = self.save_path_textedit.text(),checked_cities=self.checked_cities, text_cities=text_cities)
            self.thread.any_signal.connect(self.update_progress_bar)
            self.thread.query_signal.connect(self.update_query)
            self.thread.start()

    def update_progress_bar(self, value):
        self.prog_bar.setValue(value)
        if self.prog_bar.value() == 100 and self.indx == 1:
            self.set_cities()
        if self.prog_bar.value() > 90 and self.indx == 2:
            print('Конец')



    def update_query(self, value):
        self.count_rows = value
        self.count_queries = QuerySetter().set_query(self.count_queries, self.my_base, self.header_label,
                                                     self.count_rows, self.ws, self.id_person, self.sh)
        print('количество запросов:',self.count_rows)

class ThreadClass(QThread):
    any_signal = pyqtSignal(int)
    query_signal = pyqtSignal(int) # Signal to communicate progress updates

    def __init__(self, urls, base_url, region_combobox, label, parent=None, index=0, folder = None, checked_cities=None, text_cities = None):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True
        self.sheets_urls = urls  # List of URLs to process
        self.base_url = base_url  # Base URL for constructing download links
        self.region_combobox = region_combobox  # Combobox for selecting regions
        self.label = label  # Label to update UI text
        self.folder = folder
        self.checked_cities = checked_cities
        self.text_cities = text_cities

    def parce(self):
        folder = self.folder
        if not os.path.exists(folder + '\export'):
            os.makedirs(folder + '\export')
        for url in self.sheets_urls:
            final_url = self.base_url + urlencode(dict(public_key=url))
            response = requests.get(final_url)
            download_url = response.json()['href']
            df = pd.read_csv(download_url, sep='|')


            df.loc[df['Адрес ОЖФ'].str.contains('^\d'), 'Адрес ОЖФ'] = df['Адрес ОЖФ'].str.slice(8)
            # print(df['Адрес ОЖФ'] )
            # Город, по которому будет выполняться фильтрация
            print("Проверка cityname_textedit")
            # if self.cityname_textedit and len(self.cityname_textedit.text()) > 2:
            if self.checked_cities is None:
                print(self.text_cities)
                if ',' in self.text_cities:
                    city_filter = f" {self.text_cities}".split(',')
                else:
                    city_filter = [f" {self.text_cities}"]
            else:
                print("cityname_textedit не введён")
                city_filter = self.checked_cities

            step_loading = int(80 / len(city_filter))
            self.progress = 10  # Initial progress percentage
            self.any_signal.emit(self.progress)
            for city in city_filter:
                self.progress += step_loading  # Initial progress percentage
                self.any_signal.emit(self.progress)
                print(url)
                # Фильтрация данных по указанному городу, используя метод str.contains
                filtered_df = df[df['Адрес ОЖФ'].str.contains(city, na=False)]

                # Группировка и агрегация
                result = filtered_df.groupby('Адрес ОЖФ').agg(
                    # address =
                    total=('Адрес ОЖФ', 'count'),
                    total_living=('Тип помещения (блока)', lambda x: (x == 'Жилое').sum()),
                    total_non_living=('Тип помещения (блока)', lambda x: (x == 'Нежилое').sum()),
                    total_living_area=('Жилая площадь в доме', 'max'),
                    total_area=('Общая площадь дома', 'max'),
                    type=('Тип дома', 'first'),
                    status=('Состояние', 'first'),
                    state_host=(
                        'Дом находится в собственности субъекта Российской Федерации и в полном объеме используется в качестве общежития',
                        'first'),
                    substate_host=(
                        'Дом находится в муниципальной собственности и в полном объеме используется в качестве общежития',
                        'first'),
                    method=('Способ управления', 'first')
                ).reset_index()

                # if len(os.listdir(folder+'\export')) == 0:
                if f'ГИС_ЖКХ_{city}.csv' not in os.listdir(folder + '\export'):
                    header = True
                else:
                    header = False
                result.to_csv(rf'{folder}\export\ГИС_ЖКХ_{city}.csv', sep=';', encoding='cp1251', header=header,
                              mode='a', index=False)
                row_size = len(result.index)
                query_size = int( row_size / 400)
                # print(query_size)
                self.query_signal.emit(query_size)

    def return_cities(self):
        return self.cities_dict

    def get_cities(self):
        """
        Retrieves and processes city data from the given sheets URLs.
        Emits progress updates as the data is processed.
        """
        self.cities_dict = {}
        self.progress = 10  # Initial progress percentage
        self.any_signal.emit(self.progress)

        step_loading = 80 / len(self.sheets_urls)  # Increment progress based on the number of URLs
        # print('длина',len(self.sheets_urls))
        # print("step loading", step_loading)

        for u, url in enumerate(self.sheets_urls):
            # Update progress after processing each URL
            # self.progress += step_loading
            # print(f"Current progress: {self.progress}")
            # self.any_signal.emit(self.progress)

            print(url)
            # Construct the final URL and fetch the data
            final_url = self.base_url + urlencode(dict(public_key=url))
            response = requests.get(final_url)
            download_url = response.json()['href']
            df = pd.read_csv(download_url, sep='|')
            split_values = df['Адрес ОЖФ'].str.split(',', expand=True)
            print(split_values[1].count())

            self.progress +=  1  # Initial progress percentage
            self.any_signal.emit(self.progress)

            row_delimeter = 1
            step_row_loading = ((step_loading / split_values[1].count()) * 10000) / len(self.sheets_urls)
            if step_row_loading < 1:
                while step_row_loading < 1:
                    step_row_loading += step_row_loading
                    print("step_row_loading", step_row_loading)

                    row_delimeter += 1
            print("step_row_loading", step_row_loading)


            self.call_count = 1
            def find_element_after(values):
                # print(values.tolist())

                if self.call_count % (10000*row_delimeter) == 0:
                    self.progress += int(step_row_loading//1)
                    print(f"Current progress: {self.progress}")
                    self.any_signal.emit(self.progress)



                self.call_count += 1  # Увеличиваем счетчик каждый раз при вызове функции
                # print(self.call_count)


                idx_city = values[values.str.contains(r'\bг\. ', na=False)].index

                if len(idx_city) > 0:
                    return values[idx_city[0]]  # Return the element containing 'г. '
                else:
                    idx_rn = values[values.str.contains(r'\bр-н\b', na=False)].index
                    if len(idx_rn) > 0:
                        idx = idx_rn[0] + 1  # Return the element after 'р-н'
                    else:
                        idx_resp = values[values.str.contains(self.region_combobox.currentText(), na=False)].index
                        if len(idx_resp) > 0:
                            idx = idx_resp[0] + 1  # Return the element after 'Респ'
                        else:
                            return np.nan

                if idx < len(values):
                    return values[idx]
                else:
                    return np.nan

            # Apply the function to find unique cities
            unique_cities = split_values.apply(find_element_after, axis=1).unique()
            print(unique_cities)

            # Add the cities to the dictionary
            for city in unique_cities:
                type_city = city.split('. ')[0]
                if type_city in self.cities_dict:
                    if city not in self.cities_dict[type_city]:
                        bisect.insort(self.cities_dict[type_city], city)  # Insert city alphabetically
                else:
                    self.cities_dict[type_city] = [city]

            self.progress = int(15 + (step_loading * (u+1)))
            self.any_signal.emit(self.progress)
        print(self.cities_dict)
        return self.cities_dict


    def run(self):
        """
        Main thread execution function. Updates the label and initiates the process of retrieving city data.
        Emits progress updates during execution.
        """
        self.label.setText("Загрузка...")  # Update UI label text during data fetching

        progress = 10  # Initial progress value
        self.any_signal.emit(progress)

        if self.index == 1:
            self.get_cities()  # If index is 1, fetch cities
        elif self.index == 2:
            # print(1234567)
            self.parce()

        # self.label.setText("Завершено")  # Update label text upon completion
        progress = 100  # Initial progress value
        self.any_signal.emit(progress)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowGisJkh()
    sys.exit(app.exec())
