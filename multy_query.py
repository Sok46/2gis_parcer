import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,QHBoxLayout,QSpinBox,QFileDialog)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import time
import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
import gspread
from gspread import Client, Spreadsheet
from add_pass_to_base import BasePassParcer

class WindowMultyQuery(QWidget):
    def __init__(self,count_queries = 250, id_person = 10):
        super().__init__()


        self.count_queries = int(count_queries)
        self.id_person = id_person
        self.my_base = BasePassParcer()

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
        self.setWindowTitle("on_cup | Многостраничная выгрузка")
        self.setUpMainWindow()
        self.show()

    def openBrowser(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=chrome_options)
        url = 'https://2gis.ru/moscow'
        self.save_path_textedit.setReadOnly(True)

        self.driver.get(url)
        self.parce_button.setEnabled(True)
        self.browser_button.setEnabled(False)
        self.actions = ActionChains(self.driver)
    def save_file(self):
        f_dialog = QFileDialog().getSaveFileName(self, "Save File", "парсинг 2гис", "csv Files (*.csv)")
        path = f_dialog[0]
        self.save_path_textedit.setText(path)

    def open_main(self):
        from main_window import MainWindow
        self.hide()
        self.w = MainWindow(self.count_queries)
        self.w.show()

    def multiParce(self):
        # url = input('вставьте ссылку на карту: ')
        count_pages = self.open_browser_spinbox.value()

        # count_pages = 7
        # url = (f'https://2gis.ru/moscow/search/%D0%B1%D0%B8%D1%80%D1%8E%D0%BB%D0%B5%D0%B2%D0%BE%20%D0%B2%D0%BE%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%BE%D0%B5%20%D0%BE%D0%BF%D1%82%D0%B8%D0%BA%D0%B0?m=37.685554%2C55.600748%2F13.33%2Fp%2F20.37%2Fr%2F-7.54')
        # file_name = 'спорт-площадки бирюлёво восточное'

        points = []
        ulitsa = []
        geos = []
        arr_lat = []
        arr_long = []
        arr_stars = []
        arr_voices = []
        type_arr = []

        # driver = webdriver.Chrome()
        # driver.get(url)
        # actions = ActionChains(driver)

        i = 1
        time.sleep(9)
        # scroll_elements = self.driver.find_element(By.CSS_SELECTOR,'#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(2) > div > div > div > div._1tdquig > div._z72pvu > div._3zzdxk > div > div > div > div._1x4k6z7 > div._5ocwns > div:nth-child(2) > svg > path')
        scroll_elements = self.driver.find_element(By.CSS_SELECTOR,'#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(1) > div > div:nth-child(2) > div > div > div > div._1tdquig > div._z72pvu > div._3zzdxk > div > div > div > div._1x4k6z7 > div._5ocwns > div._n5hmn94 > svg > path')
        scr_el = self.driver.find_element(By.CLASS_NAME, '_1rkbbi0x')
        # scroll_element = scroll_elements[]
        file_name = ' хозмаги Шарыпово'
        print(file_name)

        while i <= count_pages:
            time.sleep(3)
            print(i)
            # names = self.driver.find_elements(By.CLASS_NAME, '_zjunba')
            items = self.driver.find_elements(By.CLASS_NAME, '_1kf6gff')
            print(len(items))
            print(self.count_queries, type(self.count_queries))
            if len(items) > int(self.count_queries):
                self.parce_button.setEnabled(False)
                self.header_label.setStyleSheet("color: red;")
                self.header_label.setText(f"У вас {self.count_queries} запросов, этого недостаточно")

                return

            print('aaa')
            j = 0
            for item in items:
                time.sleep(0.5)
                try:
                    type_item = item.find_element(By.CLASS_NAME, '_1idnaau').text
                except:
                    type_item = ''


                if type_item == 'Город':
                    continue
                else:
                    j += 1

                    name = item.find_element(By.CLASS_NAME, '_zjunba')

                    name.click()

                    try:
                        name = name.text
                    except:
                        name = 'error'
                    print(('ccc'))
                    time.sleep(0.5)
                    try:
                        street = self.driver.find_element(By.CSS_SELECTOR,
                                                     '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1b96w9b > div:nth-child(2) > div._t0tx82 > div._8sgdp4 > div > div:nth-child(1) > div._49kxlr > div > div:nth-child(2) > div:nth-child(1)').text
                    except:
                        street = "-"
                    print(('ddd'))
                    try:
                        descr = self.driver.find_element(By.CLASS_NAME, '_1p8iqzw').text
                    except:
                        descr = "-"

                    try:
                        stars = self.driver.find_element(By.CSS_SELECTOR,
                                                    '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._146hbp5 > div > div._y10azs').text
                    except:
                        stars = '-'
                    try:
                        count_voices = self.driver.find_element(By.CSS_SELECTOR,
                                                           '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._146hbp5 > div > div._jspzdm').text
                    except:
                        count_voices = '-'
                    # print(driver.current_url)
                    lat_right = str(self.driver.current_url).split('.')[2].split('&')[0].split('?')[0].split('%')[0]
                    # print(lat_right)
                    lat_left = str(self.driver.current_url).split('.')[1][-2:]
                    lat = str(lat_left) + '.' + str(lat_right)

                    long_right = str(self.driver.current_url).split('.')[3].split('&')[0].split('?')[0].split('%')[0]
                    long_left = str(self.driver.current_url).split('.')[2][-2:]

                    long = str(long_left) + '.' + str(long_right)


                    print(lat, long)
                    type_arr.append(type_item)
                    arr_lat.append(lat)
                    arr_long.append(long)

                    geos.append(descr)
                    ulitsa.append(street)
                    arr_stars.append(stars)
                    arr_voices.append(count_voices)
                    points.append(name)

            self.actions.move_to_element(scroll_elements).perform()

            time.sleep(1)

            # actions.click().perform()
            if i < count_pages:
                scroll_elements.click()

                print('page= ', i)
            else:
                pass
            i += 1

            df = pd.DataFrame({'name': points, 'type': type_arr, 'descr': geos, 'ulitsa': ulitsa, 'stars': arr_stars,
                               'count_voices': arr_voices, 'lat': arr_lat, 'long': arr_long})
            df.to_csv(self.save_path_textedit.text(), sep=';',
                      encoding='utf8', index=False)
            print('csv cheeeck')

            self.count_queries -= j

            print(self.count_queries)
            self.header_label.setText(f"У вас {self.count_queries} запросов")
            print(self.ws)
            print(self.id_person)
            print(int(self.count_queries))
            self.my_base.set_queries(self.ws, int(self.id_person), self.sh, int(self.count_queries))
            # self.my_base.set_queries(self.ws, int(self.id_person), int(self.count_queries))




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

        self.browser_button = QPushButton("Открыть браузер")
        button_group.addButton(self.browser_button)
        self.browser_button.setEnabled(True)
        self.main_v_box.addWidget(self.browser_button)

        question_label = QLabel("Введите необходимое количество страниц для парсинга")
        self.main_v_box.addWidget(question_label)
        self.main_v_box.addLayout(self.main_h_box)
        self.main_v_box.addLayout(self.back_h_box)
        self.open_browser_spinbox = QSpinBox()
        self.open_browser_spinbox.setMaximumWidth(100)
        self.open_browser_spinbox.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.open_browser_spinbox.setMinimum(2)
        # button_group.addButton(self.open_browser_lineEdit)
        self.main_h_box.addWidget(self.open_browser_spinbox)
        self.back_h_box.addWidget(self.back_button)



        self.parce_button = QPushButton("Начать парсинг")
        button_group.addButton(self.parce_button)
        self.parce_button.setEnabled(False)
        self.main_h_box.addWidget(self.parce_button)

        self.main_v_box.addWidget(self.confirm_button)
        self.setLayout(self.main_v_box)

        seach_action.triggered.connect(self.save_file)
        self.back_button.clicked.connect(self.open_main)
        self.browser_button.clicked.connect(self.openBrowser)
        self.parce_button.clicked.connect(self.multiParce)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowMultyQuery()
    sys.exit(app.exec())