import sys
import logging
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,QHBoxLayout,QFileDialog,
                             QComboBox,QCheckBox,QGridLayout,QGroupBox,QScrollArea, QProgressBar, QMessageBox)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QCoreApplication, QSize, QTimer
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
import traceback

from query_setter import QuerySetter
from loading_window import LoadingWindow

# Настройка логирования
logging.basicConfig(
    filename='urban_parser.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WindowGisJkh(QWidget):
    def __init__(self,count_queries = 25, id_person = 10):
        try:
            super().__init__()
            logger.info("Инициализация окна МКД/ИЖС")

            self.coinIcon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "coin.png")
            if not os.path.exists(self.coinIcon_path):
                logger.error(f"Файл иконки не найден: {self.coinIcon_path}")
                raise FileNotFoundError(f"Файл иконки не найден: {self.coinIcon_path}")
            self.coinIcon = QIcon(self.coinIcon_path)

            self.count_queries = int(count_queries)
            self.id_person = id_person
            self.my_base = BasePassParcer()
            self.cities_dict = {}
            self.count_rows = 0

            self.stage = 0
            self.checked_cities = None
            tkn = "y0_AgAAAAAGvkyVAAyD3AAAAAESV2AkAABx7BX4XRNEv7zh0HWaFEzZX1T2nA"
            try:
                self.y = yadisk.YaDisk(token=tkn)
                logger.info("Успешное подключение к Диску")
            except Exception as e:
                logger.error(f"Ошибка подключения к Диску: {str(e)}")
                QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к ГИС ЖКХ. Проверьте подключение к интернету.")
                raise

            self.gis_folder = "/ГИС ЖКХ/Сведения_об_объектах_жилищного_фонда_на_15-09-2024"
            self.base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'

            self.selected_cities = []
            self.loading_window = LoadingWindow(self)

            self.initializeUI()
            self.google_sheet_login()
            logger.info("Окно МКД/ИЖС успешно инициализировано")

        except Exception as e:
            logger.error(f"Критическая ошибка при инициализации: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Критическая ошибка", f"Произошла ошибка при запуске: {str(e)}")
            raise

    def google_sheet_login(self):
        try:
            logger.info("Подключение к Google Sheets")
            self.googe_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
            service_account_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "google_service_account.json")
            
            if not os.path.exists(service_account_path):
                logger.error(f"Файл учетных данных Google не найден: {service_account_path}")
                raise FileNotFoundError(f"Файл учетных данных Google не найден: {service_account_path}")
                
            gc: Client = gspread.service_account(service_account_path)
            self.sh: Spreadsheet = gc.open_by_url(self.googe_sheet_url)
            self.ws = self.sh.sheet1
            logger.info("Успешное подключение к Google Sheets")
        except Exception as e:
            logger.error(f"Ошибка подключения к Google Sheets: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к Google Sheets. Проверьте подключение к интернету и наличие файла учетных данных.")
            raise

    def initializeUI(self):
        """Set up the application's GUI."""
        self.setWindowTitle("Urban parser | Выгрузка домов")
        self.setUpMainWindow()
        self.show()

    def get_gis_folders(self):
        """Получает список папок из директории ГИС ЖКХ"""
        try:
            folders = []
            for item in self.y.listdir("/ГИС ЖКХ"):
                if item['type'] == 'dir':
                    folder_name = str(item['name']).replace("Сведения_об_объектах_жилищного_фонда_на_","")
                    folders.append(folder_name)
            return sorted(folders)
        except Exception as e:
            logger.error(f"Ошибка при получении списка папок: {str(e)}")
            return []

    def on_folder_changed(self, folder_name):
        """Обработчик изменения выбранной папки"""
        try:
            self.gis_folder = f"/ГИС ЖКХ/Сведения_об_объектах_жилищного_фонда_на_{folder_name}"
            logger.info(f"Выбрана папка: {self.gis_folder}")
            
            # Очищаем текущий список регионов
            self.region_combobox.clear()
            
            # Обновляем список регионов
            self.set_regions()
            
            # Очищаем текущий список городов
            self.cities_dict = {}
            self.clearLayout(self.load_city_layout)
            
            # Восстанавливаем базовую структуру load_city_layout
            add_cities_button = QPushButton("Подгрузить Населённые пункты")
            self.load_city_layout.addWidget(add_cities_button)
            
            cityname_label = QLabel("Либо введите название населённого пункта самостоятельно")
            cityname_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
            self.load_city_layout.addWidget(cityname_label)
            
            self.cityname_textedit = QLineEdit()
            self.cityname_textedit.setPlaceholderText("Например: г. Махачкала")
            self.load_city_layout.addWidget(self.cityname_textedit)
            
            # Подключаем обработчики событий
            add_cities_button.clicked.connect(self.start_city_thread)
            self.cityname_textedit.textChanged.connect(self.change_directory)
            
        except Exception as e:
            logger.error(f"Ошибка при смене папки: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить список регионов: {str(e)}")

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

    def set_regions(self):
        """Заполняем комбобокс регионами"""
        try:
            regions = []
            for item in self.y.listdir(self.gis_folder):
                file = f"path: {item['path']}"
                region = file.split('Сведения по ОЖФ ')[1].split(' на ')[0]
                regions.append(region)
            
            # Добавляем уникальные регионы в комбобокс
            self.region_combobox.addItems(sorted(list(set(regions))))
            logger.info(f"Список регионов обновлен: {len(regions)} регионов")
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка регионов: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить список регионов: {str(e)}")

    def get_selected_regions(self):
        self.sheets_urls = []
        for item in self.y.listdir(self.gis_folder):
            print(repr(self.region_combobox.currentText()))
            print(repr(item['path']))
            if self.region_combobox.currentText() in f"{item['path']}".strip():
                print(f"{item['path']}")
                sheet_url = item['public_url']
                print(sheet_url)
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
        i = 0
        for i, checkbox in enumerate(self.findChildren(QCheckBox)):
            checkbox.setChecked(status)
        # self.checkBox_counter = i+1
        # print(self.checkBox_counter)
        # self.checkBox_counter = len()


    def set_cities(self): #Вставляет полученные города из get cities в группу
        self.cities_dict = self.thread.cities_dict
        self.cities_count = self.thread.cities_count
        self.clearLayout(self.load_city_layout)

        city_layout = QVBoxLayout()
        self.download_city_butt = QPushButton("Выгрузить названия")
        self.download_city_butt.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.download_city_butt.setStyleSheet("""
            QPushButton { text-align: right; }
            QPushButton:pressed { padding-right: 3px; }
        """)
        self.update_download_button_text()  # Обновляем текст кнопки
        self.download_city_butt.clicked.connect(self.download_cities)  # Подключаем сигнал
        city_layout.addWidget(self.download_city_butt)
        city_layout.addWidget(self.all_checkboxes)

        for header in self.cities_dict.keys():
            group = QGroupBox(header)
            myFont = QFont()
            myFont.setBold(True)
            group.setFont(myFont)
            layout = QVBoxLayout()

            for city in self.cities_dict[header]:
                count = self.cities_count.get(city, 0)
                checkbox = QCheckBox(f"{city} ({count} помещений)")
                myFont.setBold(False)
                checkbox.setFont(myFont)
                layout.addWidget(checkbox)
                checkbox.checkStateChanged.connect(self.on_checkbox_state_changed)
            group.setLayout(layout)

            city_layout.addWidget(group)

        self.city_group.setLayout(city_layout)
        self.scroll.setWidget(self.city_group)

    def download_cities(self):
        cities_data = []
        for header in self.cities_dict.keys():
            for city in self.cities_dict[header]:
                count = self.cities_count.get(city, 0)
                cities_data.append({"город": city, "количество_жил.пом": count})
                
        queries_needed = round(len(cities_data)/2)
        check_query = QuerySetter().check_query(self.count_queries, queries_needed, self.header_label)
        if check_query:
            df = pd.DataFrame(cities_data)
            df.to_csv(self.save_path_textedit.text() + '/cities.csv', index=False, encoding='cp1251', sep=';')
            self.count_queries = QuerySetter().set_query(self.count_queries, self.my_base, self.header_label, queries_needed, self.ws, self.id_person, self.sh)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
    # Тарифная сетка
    def calculate_queries_by_tariff(self, rows):
        tariff_ranges = [
            (0, 10, 2),
            (11, 100, 10),
            (101, 1000, 20),
            (1001, 5000, 50),
            (5001, 10000, 100),
            (10001, 50000, 150),
            (50001, 100000, 250),
            (100001, 500000, 350),
            (500001, 1000000, 500)
        ]
        
        if rows > 1000000:
            return 2000
            
        for min_rows, max_rows, queries in tariff_ranges:
            if min_rows <= rows <= max_rows:
                return queries
                
        return 0

    def on_checkbox_state_changed(self, state):
        # Получаем все тексты активированных чекбоксов
        self.selected_cities = []
        self.total_queries = 0
        
        for group in self.findChildren(QGroupBox):
            for checkbox in group.findChildren(QCheckBox):
                if checkbox.isChecked() and checkbox != self.all_checkboxes:  # Пропускаем чекбокс "выбрать все"
                    # Извлекаем название города и количество строк
                    city_text = checkbox.text()
                    city_name = city_text.split(" (")[0]
                    rows = int(city_text.split("(")[1].split(" ")[0])
                    # Считаем запросы для каждого города отдельно
                    self.total_queries += self.calculate_queries_by_tariff(rows)
                    self.selected_cities.append(city_name)
                    
        self.checked_cities = set(self.selected_cities)
        
        # Обновляем текст кнопки и её состояние
        if self.checked_cities:
            self.browser_button.setText(f"Получить дома ({self.total_queries})")
            self.browser_button.setIcon(self.coinIcon)
            self.browser_button.setIconSize(QSize(15, 15))
            self.browser_button.setEnabled(True)
            self.browser_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.browser_button.setStyleSheet("""
                QPushButton { 
                    text-align: right; 
                    padding-right: 5px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 16px;
                    border-radius: 5px;
                    min-height: 30px;
                }
                QPushButton:hover { 
                    background-color: #45a049;
                }
                QPushButton:pressed { 
                    padding-right: 8px;
                    background-color: #3d8b40;
                }
            """)
        else:
            self.browser_button.setText("Получить дома")
            self.browser_button.setIcon(QIcon())
            self.browser_button.setEnabled(False)
            self.browser_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.browser_button.setStyleSheet("""
                QPushButton { 
                    text-align: center;
                    padding: 5px;
                    font-size: 14px;
                    min-height: 30px;
                }
            """)
            
        self.enabled_checkbox()

    def save_file(self):
        f_dialog = QFileDialog().getExistingDirectory()
        # f_dialog = QFileDialog().getSaveFileName(self, "Save File", "парсинг 2гис", "csv Files (*.csv)")
        path = f_dialog
        self.save_path_textedit.setText(path)

    def open_main(self):
        from main_window import MainWindow
        self.loading_window = LoadingWindow()  # Создаем новое окно каждый раз
        self.loading_window.show()
        QApplication.processEvents()  # Обрабатываем события, чтобы окно загрузки отобразилось
        QTimer.singleShot(100, lambda: self._complete_switch(MainWindow, self.count_queries))

    def _complete_switch(self, window_class, *args):
        self.w = window_class(*args)
        self.w.show()
        self.hide()
        if hasattr(self, 'loading_window'):
            self.loading_window.close()

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


    def setUpMainWindow(self):
        # self.sheets_urls = [] #ссылки на csv Файлы
        # self.header_label = QLabel(f"У вас {self.count_queries} запросов")
        self.header_label = QLabel(
            f'У вас {self.count_queries} <img src={self.coinIcon_path} width="30" height="30" style="vertical-align: top;">'
        )
        self.header_label.setFont(QFont("Arial", 18))
        self.header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Выберете папку для выгрузки:")
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
        seach_action = self.save_path_textedit.addAction(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "folder_icon.png")), QLineEdit.ActionPosition.LeadingPosition)

        self.save_path_textedit.setPlaceholderText('Укажите путь для выходных csv ...')
        self.main_v_box.addWidget(self.save_path_textedit)

        # Создаем два вертикальных layout'а для столбцов
        columns_layout = QHBoxLayout()
        
        # Первый столбец (регионы)
        region_column = QVBoxLayout()
        region_label = QLabel("Выберете регион")
        region_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        region_column.addWidget(region_label)
        
        self.region_combobox = QComboBox()
        self.set_regions()
        region_column.addWidget(self.region_combobox)
        
        # Второй столбец (папки)
        folder_column = QVBoxLayout()
        folder_label = QLabel("Сведения жилищного фонда на:")
        folder_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        folder_column.addWidget(folder_label)
        
        self.folder_combobox = QComboBox()
        self.folder_combobox.addItems(self.get_gis_folders())
        self.folder_combobox.currentTextChanged.connect(self.on_folder_changed)
        folder_column.addWidget(self.folder_combobox)
        
        # Добавляем столбцы в горизонтальный layout
        columns_layout.addLayout(region_column)
        columns_layout.addLayout(folder_column)
        
        # Добавляем общий layout в основной
        self.main_v_box.addLayout(columns_layout)

        self.city_group = QGroupBox("Населённые пункты")
        self.load_city_layout = QVBoxLayout()

        add_cities_button = QPushButton("Подгрузить Населённые пункты")
        self.prog_bar = QProgressBar()

        self.scroll = QScrollArea()

        # self.scroll.setWidget(add_cities_button)
        # self.scroll.setWidgetResizable(True)
        # self.scroll.setBaseSize(50,5)
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

        self.main_v_box.addWidget(self.scroll)
        self.main_v_box.addWidget(self.prog_bar)
        # self.main_v_box.setEnabled(False)

        self.download_city_butt = QPushButton("Выгрузить названия")
        self.all_checkboxes = QCheckBox("Выбрать все")


        self.browser_button = QPushButton("Получить дома")
        self.browser_button.setEnabled(False)
        self.browser_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.browser_button.setStyleSheet("""
            QPushButton { 
                text-align: center;
            }
        """)
        self.main_v_box.addWidget(self.browser_button)
        self.main_v_box.addWidget(self.back_button)


        self.change_directory()
        self.setLayout(self.main_v_box)

        seach_action.triggered.connect(self.save_file)
        self.back_button.clicked.connect(self.open_main)
        # self.browser_button.clicked.connect(self.parce)
        self.browser_button.clicked.connect(self.start_parce_thread)

        add_cities_button.clicked.connect(self.start_city_thread)
        # add_cities_button.clicked.connect(self.set_cities)
        self.download_city_butt.clicked.connect(self.download_cities)
        self.all_checkboxes.checkStateChanged.connect(self.select_all_checkboxes)


        #Сигналы для отображения кнопок
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

            self.thread = ThreadClass(self.sheets_urls, self.base_url, self.region_combobox,self.header_label, index=self.indx, folder = self.save_path_textedit.text(),checked_cities=self.checked_cities, text_cities=text_cities, total_queries=self.total_queries)
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

    # self.parce_button.clicked.connect(self.parce)

    def update_download_button_text(self):
        cities = []
        for header in self.cities_dict.keys():
            for city in self.cities_dict[header]:
                cities.append(city)
        queries_needed = round(len(cities)/2)
        self.download_city_butt.setText(f"Выгрузить названия ({queries_needed} )")
        self.download_city_butt.setIcon(self.coinIcon)
        self.download_city_butt.setIconSize(QSize(15, 15))


class ThreadClass(QThread):
    any_signal = pyqtSignal(int)
    query_signal = pyqtSignal(int) # Signal to communicate progress updates

    def __init__(self, urls, base_url, region_combobox, label, parent=None, index=0, folder = None, checked_cities=None, text_cities = None,total_queries = None):
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
        self.total_queries = total_queries

    def parce(self):
        folder = self.folder
        if not os.path.exists(folder + '\export'):
            os.makedirs(folder + '\export')
        self.query_signal.emit(self.total_queries)
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
                print('отфильтровано')

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
                print(f"gorod {city}")
                city = city.replace('/','-')
                print(f"gorod {city}")
                if f'ГИС_ЖКХ_{city}.csv' not in os.listdir(folder + '\export'):
                    header = True
                else:
                    header = False
                print(f"header")
                result.to_csv(rf'{folder}\export\ГИС_ЖКХ_{city}.csv', sep=';', encoding='cp1251', header=header,
                              mode='a', index=False)
                print(f"export")
                # row_size = len(result.index)
                # query_size = int( row_size / 400)
                # print(self.total_queries)



    def return_cities(self):
        return self.cities_dict

    def get_cities(self):
        """
        Retrieves and processes city data from the given sheets URLs.
        Emits progress updates as the data is processed.
        """
        self.cities_dict = {}
        self.cities_count = {}  # Словарь для хранения количества упоминаний каждого города
        self.progress = 10  # Initial progress percentage
        self.any_signal.emit(self.progress)

        step_loading = 80 / len(self.sheets_urls)

        for u, url in enumerate(self.sheets_urls):
            print(url)
            final_url = self.base_url + urlencode(dict(public_key=url))
            response = requests.get(final_url)
            download_url = response.json()['href']
            df = pd.read_csv(download_url, sep='|')
            split_values = df['Адрес ОЖФ'].str.split(',', expand=True)
            print(split_values[1].count())

            self.progress +=  1
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
                if self.call_count % (10000*row_delimeter) == 0:
                    self.progress += int(step_row_loading//1)
                    print(f"Current progress: {self.progress}")
                    self.any_signal.emit(self.progress)

                self.call_count += 1

                idx_city = values[values.str.contains(r'\bг\. ', na=False)].index

                if len(idx_city) > 0:
                    return values[idx_city[0]]
                else:
                    idx_rn = values[values.str.contains(r'\bр-н\b', na=False)].index
                    if len(idx_rn) > 0:
                        idx = idx_rn[0] + 1
                    else:
                        idx_resp = values[values.str.contains(self.region_combobox.currentText(), na=False)].index
                        if len(idx_resp) > 0:
                            idx = idx_resp[0] + 1
                        else:
                            return np.nan

                if idx < len(values):
                    return values[idx]
                else:
                    return np.nan

            # Подсчитываем количество упоминаний каждого города
            cities_series = split_values.apply(find_element_after, axis=1)
            city_counts = cities_series.value_counts()
            
            # Обновляем общий словарь с количеством упоминаний
            for city, count in city_counts.items():
                if city is not np.nan:
                    if city in self.cities_count:
                        self.cities_count[city] += count
                    else:
                        self.cities_count[city] = count

            # Обновляем словарь городов с учетом типов
            for city in city_counts.index:
                if city is not np.nan:
                    type_city = city.split('. ')[0]
                    if type_city in self.cities_dict:
                        if city not in self.cities_dict[type_city]:
                            bisect.insort(self.cities_dict[type_city], city)
                    else:
                        self.cities_dict[type_city] = [city]

            self.progress = int(15 + (step_loading * (u+1)))
            self.any_signal.emit(self.progress)

        print(self.cities_dict)
        return self.cities_dict, self.cities_count


    def run(self):
        """
        Main thread execution function. Updates the label and initiates the process of retrieving city data.
        Emits progress updates during execution.
        """
        # self.label.setText("Загрузка...")  # Update UI label text during data fetching

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