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


class WindowGisJkh(QWidget):
    def __init__(self,count_queries = 25, id_person = 10):
        super().__init__()
        self.stage = 0 # включение кнопок по ходу выполнения программы
        self.checked_cities = None
        self.count_queries = int(count_queries)
        self.id_person = id_person
        self.my_base = BasePassParcer()

        tkn = "y0_AgAAAAAGvkyVAAyD3AAAAAESV2AkAABx7BX4XRNEv7zh0HWaFEzZX1T2nA"
        self.y = yadisk.YaDisk(token=tkn)
        self.gis_folder = "/ГИС ЖКХ/Сведения_об_объектах_жилищного_фонда_на_15-09-2024" #Путь к папке на Яндексе
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'

        self.initializeUI()
        self.google_sheet_login()



    def google_sheet_login(self):
        self.googe_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        self.sh: Spreadsheet = gc.open_by_url(self.googe_sheet_url)
        self.ws = self.sh.sheet1

    def initializeUI(self):
        """Set up the application's GUI."""
        # self.setMaximumSize(310, 130)
        self.setWindowTitle("on_cup | Выгрузка домов")
        self.setUpMainWindow()
        self.show()

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
        self.cities_dict = {}
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

    def set_cities(self): #Вставляет полученные города из get cities в группу
        self.cities_dict = self.thread.cities_dict
        self.clearLayout(self.load_city_layout)
        # self.get_cities()



        city_layout = QVBoxLayout()
        city_layout.addWidget(self.download_city_butt)

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

        self.scroll.setWidget(self.city_group)
        # self.download_city_butt.clicked.connect(self.download_cities())
        # self.scroll.setLayout(white_layout)

        # self.main_v_box.addWidget(self.scroll)

            # self.city_combobox.addItems(unique_cities)
    def download_cities(self):
        cities = []
        for header in  self.cities_dict.keys():
            for city in self.cities_dict[header]:
                cities.append(city)
        df = pd.DataFrame(cities, columns=["города"])
        df.to_csv(self.save_path_textedit.text() + '/cities.csv', index=False, encoding='cp1251')




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

    def open_main(self):
        from main_window import MainWindow
        self.hide()
        self.w = MainWindow(self.count_queries)
        self.w.show()

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





    def setUpMainWindow(self):
        # self.sheets_urls = [] #ссылки на csv Файлы
        self.header_label = QLabel(f"У вас {self.count_queries} запросов")
        self.header_label.setFont(QFont("Arial", 18))
        self.header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Выберете действие")
        question_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        button_group = QButtonGroup(self)
        # button_group.buttonClicked.connect(
        #     self.checkboxClicked)

        self.confirm_button = QPushButton("Завершить программу")
        self.confirm_button.setEnabled(False)
        # self.confirm_button.clicked.connect(self.stopDriver)
        # self.confirm_button.clicked.connect(self.close)

        self.back_button = QPushButton("Назад")
        self.back_button.setEnabled(True)


        self.main_v_box = QVBoxLayout()
        self.main_v_box.addWidget(self.header_label)
        self.main_v_box.addWidget(question_label)

        self.main_h_box = QHBoxLayout()
        self.back_h_box = QHBoxLayout()

        self.save_path_textedit = QLineEdit()
        # self.link_url.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.save_path_textedit.setClearButtonEnabled(True)
        # self.link_url.addAction(QIcon('icons/folder_icon.png'), QLineEdit.ActionPosition.LeadingPosition)
        seach_action = self.save_path_textedit.addAction(QIcon('icons/folder_icon.png'), QLineEdit.ActionPosition.LeadingPosition)

        self.save_path_textedit.setPlaceholderText('Укажите путь для выходных csv ...')
        self.main_v_box.addWidget(self.save_path_textedit)

        region_label = QLabel("Выберете регион")
        region_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_v_box.addWidget(region_label)
        self.region_combobox = QComboBox()
        self.set_regions()
        self.main_v_box.addWidget(self.region_combobox)

        self.city_group = QGroupBox("Населённые пункты")
        self.load_city_layout = QVBoxLayout()

        add_cities_button = QPushButton("Подгрузить Населённые пункты")
        self.prog_bar = QProgressBar()

        self.scroll = QScrollArea()

        # self.scroll.setWidget(add_cities_button)
        self.scroll.setWidgetResizable(True)
        self.scroll.setBaseSize(50,5)
        self.scroll.baseSize()


        self.load_city_layout.addWidget(add_cities_button)
        self.load_city_layout.addWidget(self.prog_bar)
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

        self.main_v_box.addWidget(self.scroll)
        # self.main_v_box.setEnabled(False)

        self.download_city_butt = QPushButton("Выгрузить названия")






        self.browser_button = QPushButton("Получить дома")
        self.browser_button.setEnabled(True)
        self.main_v_box.addWidget(self.browser_button)
        self.main_v_box.addWidget(self.back_button)


        self.change_directory()
        self.setLayout(self.main_v_box)

        seach_action.triggered.connect(self.save_file)
        self.back_button.clicked.connect(self.open_main)
        self.browser_button.clicked.connect(self.parce)

        add_cities_button.clicked.connect(self.start_auth_thread)
        # add_cities_button.clicked.connect(self.set_cities)
        self.download_city_butt.clicked.connect(self.download_cities)


        #Сигналы для отображения кнопок
        # self.browser_button.clicked.connect(self.change_directory)
        self.cityname_textedit.textChanged.connect(self.change_directory)
        self.save_path_textedit.textChanged.connect(self.change_directory)


    def start_auth_thread(self):
        self.get_selected_regions()
        self.thread = ThreadClass(self.sheets_urls, self.base_url, self.region_combobox,self.header_label, index=1)
        self.thread.any_signal.connect(self.update_progress_bar)
        self.thread.start()


    def update_progress_bar(self, value):
        self.prog_bar.setValue(value)
        if self.prog_bar.value() == 100:
            self.set_cities()
        # self.parce_button.clicked.connect(self.parce)

class ThreadClass(QThread):
    any_signal = pyqtSignal(int)  # Signal to communicate progress updates


    def __init__(self, urls, base_url, region_combobox, label, parent=None, index=0):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True
        self.sheets_urls = urls  # List of URLs to process
        self.base_url = base_url  # Base URL for constructing download links
        self.region_combobox = region_combobox  # Combobox for selecting regions
        self.label = label  # Label to update UI text
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
        print('длина',len(self.sheets_urls))
        print("step loading", step_loading)

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

        self.label.setText("Завершено")  # Update label text upon completion
        progress = 100  # Initial progress value
        self.any_signal.emit(progress)








if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowGisJkh()
    sys.exit(app.exec())