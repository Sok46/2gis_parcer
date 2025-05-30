import sys
import logging
import os
from typing import List, Dict, Optional, Tuple
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, 
                            QButtonGroup, QVBoxLayout, QHBoxLayout, QSpinBox, QFileDialog)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize
import time
import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
import gspread
from gspread import Client, Spreadsheet
from add_pass_to_base import BasePassParcer
from query_setter import QuerySetter

# Настройка логирования
logging.basicConfig(
    filename='urban_parser.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Константы
CONFIG = {
    'google_sheet_url': 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0',
    'service_account_path': os.path.join('icons', 'google_service_account.json'),
    'default_url': 'https://2gis.ru/moscow',
    'wait_time': 3
}

class WindowMultyQuery(QWidget):
    def __init__(self, count_queries: int = 250, id_person: int = 10):
        super().__init__()
        self.count_queries = int(count_queries)
        self.id_person = id_person
        self.my_base = BasePassParcer()
        self.driver: Optional[webdriver.Chrome] = None
        self.actions: Optional[ActionChains] = None
        
        try:
            self.initializeUI()
            self.google_sheet_login()
        except Exception as e:
            logger.error(f"Ошибка при инициализации: {str(e)}")
            raise

    def google_sheet_login(self) -> None:
        """Подключение к Google Sheets."""
        try:
            if not os.path.exists(CONFIG['service_account_path']):
                raise FileNotFoundError(f"Файл учетных данных не найден: {CONFIG['service_account_path']}")
                
            gc: Client = gspread.service_account(CONFIG['service_account_path'])
            self.sh: Spreadsheet = gc.open_by_url(CONFIG['google_sheet_url'])
            self.ws = self.sh.sheet1
            logger.info("Успешное подключение к Google Sheets")
        except Exception as e:
            logger.error(f"Ошибка подключения к Google Sheets: {str(e)}")
            raise

    def initializeUI(self) -> None:
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("Urban parser | Многостраничная выгрузка")
        self.setUpMainWindow()
        self.show()

    def openBrowser(self) -> None:
        """Открытие браузера и инициализация драйвера."""
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get(CONFIG['default_url'])
            self.save_path_textedit.setReadOnly(True)
            self.parce_button.setEnabled(True)
            self.browser_button.setEnabled(False)
            self.actions = ActionChains(self.driver)
            logger.info("Браузер успешно открыт")
        except Exception as e:
            logger.error(f"Ошибка при открытии браузера: {str(e)}")
            raise

    def save_file(self) -> None:
        """Сохранение пути к файлу."""
        try:
            f_dialog = QFileDialog().getSaveFileName(self, "Save File", "парсинг 2гис", "csv Files (*.csv)")
            path = f_dialog[0]
            self.save_path_textedit.setText(path)
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {str(e)}")
            raise

    def open_main(self) -> None:
        """Возврат в главное окно."""
        try:
            from main_window import MainWindow
            self.hide()
            self.w = MainWindow(self.count_queries, self.id_person)
            self.w.show()
        except Exception as e:
            logger.error(f"Ошибка при открытии главного окна: {str(e)}")
            raise

    def get_element_text(self, selector: str, default: str = '-') -> str:
        """Получение текста элемента с обработкой ошибок."""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector).text
        except NoSuchElementException:
            return default

    def parse_coordinates(self, url: str) -> Tuple[str, str]:
        """Парсинг координат из URL."""
        try:
            parts = url.split('.')
            lat_right = parts[2].split('&')[0].split('?')[0].split('%')[0]
            lat_left = parts[1][-2:]
            long_right = parts[3].split('&')[0].split('?')[0].split('%')[0]
            long_left = parts[2][-2:]
            
            return f"{lat_left}.{lat_right}", f"{long_left}.{long_right}"
        except Exception as e:
            logger.error(f"Ошибка при парсинге координат: {str(e)}")
            return '-', '-'

    def parse_item_data(self, item: WebElement) -> Dict[str, str]:
        """Парсинг данных одного элемента."""
        try:
            type_item = item.find_element(By.CLASS_NAME, '_1idnaau').text
        except NoSuchElementException:
            type_item = '-'

        if type_item in ['Город', 'Памятные доски']:
            return {}

        name_element = item.find_element(By.CLASS_NAME, '_zjunba')
        name_element.click()
        time.sleep(0.5)

        name = name_element.text if name_element.text else 'error'
        
        # Получаем данные с использованием существующих селекторов
        street = self.get_element_text('#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1b96w9b > div:nth-child(2) > div._t0tx82 > div._8sgdp4 > div > div:nth-child(1) > div._49kxlr > div > div:nth-child(2) > div:nth-child(1) > span')
        if street == '-':
            street = self.get_element_text('#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._1dbpexg')

        descr = self.get_element_text('#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1b96w9b > div:nth-child(2) > div._t0tx82 > div._8sgdp4 > div > div:nth-child(1) > div._49kxlr > div > div:nth-child(2) > div:nth-child(1) > div')
        if descr == '-':
            descr = self.get_element_text('#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div:nth-child(5) > span')

        stars = self.get_element_text('#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._146hbp5 > div > div._y10azs')
        voices = self.get_element_text('#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._146hbp5 > div > div._jspzdm')

        lat, long = self.parse_coordinates(self.driver.current_url)
        url = self.driver.current_url

        return {
            'name': name,
            'type': type_item,
            'descr': descr,
            'ulitsa': street,
            'stars': stars,
            'count_voices': voices,
            'lat': lat,
            'long': long,
            'url': url
        }

    def save_data(self, data: Dict[str, List], page: int) -> None:
        """Сохранение данных в файл."""
        try:
            df = pd.DataFrame(data)
            if page == 1:
                df.to_csv(self.save_path_textedit.text(), sep=';', encoding='utf-8', index=False)
            else:
                df.to_csv(self.save_path_textedit.text(), sep=';', encoding='utf-8', mode='a', header=False, index=False)
            logger.info(f"Данные страницы {page} успешно сохранены")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных страницы {page}: {str(e)}")
            try:
                df.to_excel(self.save_path_textedit.text(), index=False)
            except Exception as excel_error:
                logger.error(f"Ошибка при сохранении в Excel: {str(excel_error)}")
                raise

    def multiParce(self) -> None:
        """Основной метод парсинга."""
        try:
            count_pages = self.open_browser_spinbox.value()
            data = {
                'name': [], 'type': [], 'descr': [], 'ulitsa': [],
                'stars': [], 'count_voices': [], 'lat': [], 'long': [], 'url': []
            }

            time.sleep(2)
            scroll_elements = self.driver.find_element(By.CSS_SELECTOR,'#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div:nth-child(1) > div > div:nth-child(2) > div > div > div > div._1tdquig > div._z72pvu > div._3zzdxk > div > div > div > div._1x4k6z7 > div._5ocwns > div._n5hmn94 > svg > path')
            scroll_elements2 = self.driver.find_element(By.CSS_SELECTOR,'#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(3) > div > div > div:nth-child(2) > div > div > div > div._1tdquig > div._z72pvu > div._3zzdxk > div > div > div > div._1x4k6z7 > div._5ocwns > div:nth-child(2) > svg')
            scr_el = self.driver.find_element(By.CLASS_NAME, '_1rkbbi0x')

            for page in range(1, count_pages + 1):
                logger.info(f"Начало парсинга страницы {page}")
                time.sleep(CONFIG['wait_time'])
                
                items = self.driver.find_elements(By.CLASS_NAME, '_1kf6gff')
                items_count = len(items)
                
                if items_count > self.count_queries:
                    self.parce_button.setEnabled(False)
                    self.header_label.setStyleSheet("color: red;")
                    self.header_label.setText(f"У вас {self.count_queries} запросов, этого недостаточно")
                    self.driver.quit()  # Закрываем браузер при недостатке запросов
                    return

                valid_items_count = 0
                for item in items:
                    item_data = self.parse_item_data(item)
                    if item_data:
                        valid_items_count += 1
                        for key in data:
                            data[key].append(item_data[key])

                if page < count_pages:
                    self.actions.move_to_element(scroll_elements).perform()
                    time.sleep(1)

                    next_click = False
                    click_counter = 0
                    while not next_click:
                        try:
                            try:
                                scroll_elements.click()
                            except:
                                self.actions.move_to_element(scroll_elements2).perform()
                                scroll_elements2.click()
                            next_click = True
                        except:
                            click_counter += 1
                            time.sleep(1)
                            continue

                self.save_data(data, page)
                
                check_query = QuerySetter().check_query(self.count_queries, valid_items_count, self.header_label)
                if check_query:
                    self.count_queries = QuerySetter().set_query(
                        self.count_queries, self.my_base, self.header_label,
                        valid_items_count, self.ws, self.id_person, self.sh
                    )

            logger.info("Парсинг успешно завершен")
            self.driver.quit()  # Закрываем браузер после успешного завершения
            self.parce_button.setEnabled(False)  # Отключаем кнопку после завершения
            self.browser_button.setEnabled(True)  # Включаем кнопку открытия браузера
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге: {str(e)}")
            if self.driver:
                self.driver.quit()  # Закрываем браузер в случае ошибки
            raise

    def setUpMainWindow(self) -> None:
        """Настройка главного окна."""
        try:
            self.coinIcon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "coin.png")
            self.header_label = QLabel(
                f'У вас {self.count_queries} <img src={self.coinIcon_path} width="30" height="30" style="vertical-align: top;">'
            )
            self.header_label.setFont(QFont("Arial", 18))
            self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            question_label = QLabel("Выберете действие")
            question_label.setAlignment(Qt.AlignmentFlag.AlignBottom)

            button_group = QButtonGroup(self)

            self.confirm_button = QPushButton("Завершить программу")
            self.confirm_button.setEnabled(False)

            self.back_button = QPushButton("Назад")
            self.back_button.setEnabled(True)

            self.main_v_box = QVBoxLayout()
            self.main_v_box.addWidget(self.header_label)
            self.main_v_box.addWidget(question_label)

            self.main_h_box = QHBoxLayout()
            self.back_h_box = QHBoxLayout()

            self.save_path_textedit = QLineEdit()
            self.save_path_textedit.setClearButtonEnabled(True)
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
            self.open_browser_spinbox.setMaximum(1000)
            self.main_h_box.addWidget(self.open_browser_spinbox)
            self.back_h_box.addWidget(self.back_button)

            self.parce_button = QPushButton("Начать парсинг")
            button_group.addButton(self.parce_button)
            self.parce_button.setEnabled(False)
            try:
                self.parce_button.setIcon(QIcon('icons/coin.png'))
                self.parce_button.setIconSize(QSize(24, 24))
                self.parce_button.setStyleSheet("""
                    QPushButton:enabled {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        padding: 10px;
                        font-size: 16px;
                        border-radius: 5px;
                        min-height: 30px;
                    }
                    QPushButton:enabled:hover {
                        background-color: #45a049;
                    }
                    QPushButton:enabled:pressed {
                        background-color: #3d8b40;
                    }
                    QPushButton:disabled {
                        background-color: #cccccc;
                        color: #666666;
                    }
                """)
            except Exception as e:
                logger.error(f"Ошибка при загрузке иконки: {str(e)}")
            self.main_h_box.addWidget(self.parce_button)

            self.main_v_box.addWidget(self.confirm_button)
            self.setLayout(self.main_v_box)

            seach_action.triggered.connect(self.save_file)
            self.back_button.clicked.connect(self.open_main)
            self.browser_button.clicked.connect(self.openBrowser)
            self.parce_button.clicked.connect(self.multiParce)

        except Exception as e:
            logger.error(f"Ошибка при настройке главного окна: {str(e)}")
            raise

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowMultyQuery()
    sys.exit(app.exec())