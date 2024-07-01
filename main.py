import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By

url = (f'https://2gis.ru/ramenskoe/search/%D0%B1%D0%B8%D0%B1%D0%BB%D0%B8%D0%BE%D1%82%D0%B5%D0%BA%D0%B8%20%D1%80%D0%B0%D0%BC%D0%B5%D0%BD%D1%81%D0%BA%D0%BE%D0%B5?m=38.218276%2C55.572913%2F13.08')
file_name = 'раменское библиотеки'


points = []
ulitsa = []
geos = []
arr_lat = []
arr_long = []
arr_stars = []
arr_voices = []
type_arr = []

driver = webdriver.Chrome()
driver.get(url)
actions = ActionChains(driver)


i=1
time.sleep(9)
scroll_elements = driver.find_element(By.CSS_SELECTOR, '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(2) > div > div > div > div._1tdquig > div._z72pvu > div._3zzdxk > div > div > div > div._1x4k6z7 > div._5ocwns > div:nth-child(2) > svg > path')
scr_el = driver.find_element(By.CLASS_NAME,'_1rkbbi0x')
# scroll_element = scroll_elements[]

while i<=2:
    time.sleep(3)
    names = driver.find_elements(By.CLASS_NAME,'_zjunba' )
    items = driver.find_elements(By.CLASS_NAME,'_1kf6gff' )


    for item in items:
        time.sleep(0.5)
        try:
            type_item = item.find_element(By.CLASS_NAME,'_1idnaau' ).text
        except:
            type_item = ''

        if type_item == 'Город':
            continue
        else:
            name = item.find_element(By.CLASS_NAME,'_zjunba' )
            name.click()
            try:
                name = name.text
            except:
                name = 'error'

            time.sleep(0.5)
            try:
                street = driver.find_element(By.CSS_SELECTOR,'#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1b96w9b > div:nth-child(2) > div._t0tx82 > div._8sgdp4 > div > div:nth-child(1) > div._49kxlr > div > div:nth-child(2) > div:nth-child(1)').text
            except:
                street = "error"
            try:
                descr = driver.find_element(By.CLASS_NAME,'_1p8iqzw').text
            except:
                descr = "error"

            try:
                stars = driver.find_element(By.CSS_SELECTOR,'#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._146hbp5 > div > div._y10azs').text
            except:
                stars = '-'
            try:
                count_voices = driver.find_element(By.CSS_SELECTOR,'#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1tfwnxl > div._146hbp5 > div > div._jspzdm').text
            except:
                count_voices = '-'
            print(driver.current_url)
            lat_right = str(driver.current_url).split('.')[2].split('&')[0].split('?')[0].split('%')[0]
            # print(lat_right)
            lat_left = str(driver.current_url).split('.')[1][-2:]
            lat = str(lat_left) + '.' + str(lat_right)

            long_right = str(driver.current_url).split('.')[3].split('&')[0].split('?')[0].split('%')[0]
            long_left = str(driver.current_url).split('.')[2][-2:]

            long = str(long_left) + '.' + str(long_right)

            print(lat,long)
            type_arr.append(type_item)
            arr_lat.append(lat)
            arr_long.append(long)

            geos.append(descr)
            ulitsa.append(street)
            arr_stars.append(stars)
            arr_voices.append(count_voices)
            points.append(name)


    actions.move_to_element(scroll_elements).perform()
    time.sleep(1)
    # actions.click().perform()
    scroll_elements.click()
    print('page= ',i)

    i += 1

    df = pd.DataFrame({'name': points,'type' : type_arr, 'descr' : geos, 'ulitsa': ulitsa, 'stars': arr_stars, 'count_voices': arr_voices, 'lat' : arr_lat, 'long': arr_long})
    df.to_csv(fr'C:\Users\sergey.biryukov\Desktop\Москва генплан конкурс\Общепит/{file_name}.csv', sep=';', encoding='utf8', index=False)

    # читаем данные из строки DataFrame
    data = pd.read_csv(rf'C:\Users\sergey.biryukov\Desktop\Москва генплан конкурс\Общепит/{file_name}.csv', sep=' ; ')
    print(data)





driver.quit()
