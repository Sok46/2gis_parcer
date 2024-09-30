import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,QHBoxLayout,QFileDialog,QComboBox)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import os
import gspread
from gspread import Client, Spreadsheet
from add_pass_to_base import BasePassParcer
import pandas as pd
import requests
from urllib.parse import urlencode
import yadisk

class WindowGisJkh(QWidget):
    def __init__(self,count_queries = 25, id_person = 10):
        super().__init__()


        self.count_queries = int(count_queries)
        self.id_person = id_person
        self.my_base = BasePassParcer()

        tkn = "y0_AgAAAAAGvkyVAAyD3AAAAAESV2AkAABx7BX4XRNEv7zh0HWaFEzZX1T2nA"
        self.y = yadisk.YaDisk(token=tkn)
        self.gis_folder = "/ГИС ЖКХ/Сведения_об_объектах_жилищного_фонда_на_15-09-2024"
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
        self.setWindowTitle("on_cup | Выгрузка маршрутов")
        self.setUpMainWindow()
        self.show()
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
            final_url = self.base_url + urlencode(dict(public_key=url))
            response = requests.get(final_url)
            download_url = response.json()['href']
            df = pd.read_csv(download_url, sep='\t')
            print(df.head(n=2))
            print(df[' Адрес ОЖФ'])
            unique_values = df[' Адрес ОЖФ'].unique()
            print(unique_values)

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
        folder = r'C:\Users\sergey.biryukov\Desktop\Крас край\Красноярский Край1\Красноярский Край\реестр домов\ГИС ЖКХ'
        if not os.path.exists(folder + '\export'):
            os.makedirs(folder + '\export')

        for i, filename in enumerate(os.listdir(folder)):
            if filename.endswith('.csv'):
                print(filename)

                path = rf'{folder}\{filename}'

                df = pd.read_csv(path, sep='|', encoding='UTF-8')

                # Удаление индекса из начала строки в колонке "address"
                # df['Адрес ОЖФ'] = df['Адрес ОЖФ'].str.slice(8)
                df.loc[df['Адрес ОЖФ'].str.contains('^\d'), 'Адрес ОЖФ'] = df['Адрес ОЖФ'].str.slice(8)
                # print(df['Адрес ОЖФ'] )

                # Город, по которому будет выполняться фильтрация
                city_filter = ' г. Назарово'

                # Фильтрация данных по указанному городу, используя метод str.contains
                filtered_df = df[df['Адрес ОЖФ'].str.contains(city_filter, na=False)]

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
                if f'ГИС_ЖКХ_{city_filter}.csv' not in os.listdir(folder + '\export'):
                    header = True

                else:
                    header = False

                result.to_csv(rf'{folder}\export\ГИС_ЖКХ_{city_filter}.csv', sep=';', encoding='utf-8', header=header,
                              mode='a', index=False)




    def setUpMainWindow(self):
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

        self.save_path_textedit.setPlaceholderText('Укажите путь для выходного csv ...')
        self.main_v_box.addWidget(self.save_path_textedit)

        region_label = QLabel("Выберете регион")
        region_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_v_box.addWidget(region_label)
        self.region_combobox = QComboBox()
        self.set_regions()
        self.main_v_box.addWidget(self.region_combobox)



        cityname_label = QLabel("Название города")
        cityname_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_v_box.addWidget(cityname_label)
        self.cityname_textedit = QLineEdit()
        self.cityname_textedit.setPlaceholderText(" г. Назарово")
        self.main_v_box.addWidget(self.cityname_textedit)


        routes_label = QLabel("Номера маршрутов для скачивания")
        routes_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_v_box.addWidget(routes_label)
        self.routes_textedit = QLineEdit()
        self.routes_textedit.setPlaceholderText("1,2,125,троллейбус 1")
        self.main_v_box.addWidget(self.routes_textedit)




        self.browser_button = QPushButton("Начать парсинг")
        self.browser_button.setEnabled(True)
        self.main_v_box.addWidget(self.browser_button)
        self.main_v_box.addWidget(self.back_button)



        self.setLayout(self.main_v_box)

        seach_action.triggered.connect(self.save_file)
        self.back_button.clicked.connect(self.open_main)
        self.browser_button.clicked.connect(self.get_cities)
        # self.parce_button.clicked.connect(self.parce)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowGisJkh()
    sys.exit(app.exec())