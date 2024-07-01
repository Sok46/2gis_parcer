import time

import requests
import pandas as pd
from bs4 import BeautifulSoup

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# url = f'https://stopgame.ru/review/p{p}?subsection=izumitelno'
# r = requests.get("https://2gis.ru/moscow/search/rhfcyjt%20%2Ctkjt?m=37.672718%2C55.735931%2F11")
url = (f'https://2gis.ru/izhevsk/search/%D0%BC%D1%83%D0%B7%D0%B5%D0%B8?m=53.279377%2C56.832811%2F12.16')
file_name = 'музеи Ижевск'


headers = requests.utils.default_headers()

headers.update(
    {
        'User-Agent': 'My User Agent 1.0',
    }
)
r = requests.get(url, headers=headers)
points = []
ulitsa = []
geos = []
arr_lat = []
arr_long = []
arr_stars = []
arr_voices = []
soup = BeautifulSoup(r.text, 'lxml')


driver = webdriver.Chrome()
driver.get(url)
actions = ActionChains(driver)


i=1
# while i <=10:
time.sleep(9)
scroll_elements = driver.find_element(By.CSS_SELECTOR, '#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(2) > div > div > div > div._1tdquig > div._z72pvu > div._3zzdxk > div > div > div > div._1x4k6z7 > div._5ocwns > div:nth-child(2) > svg > path')
print(scroll_elements)
scr_el = driver.find_element(By.CLASS_NAME,'_1rkbbi0x')
# scroll_element = scroll_elements[]

while i<=78:
    time.sleep(3)
    # actions.move_to_element(scroll_elements)


    # element_height = driver.execute_script("return arguments[0].scrollHeight;", scroll_element)
    names = driver.find_elements(By.CLASS_NAME,'_zjunba' )

    for name in names:
        time.sleep(0.5)
        name.click()

        try:
            name = name.text
        except:
            name = 'error'

        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        # scr_el.send_keys(Keys.DOWN)
        time.sleep(0.5)
        try:
            street = driver.find_element(By.CSS_SELECTOR,'#root > div > div > div._1sf34doj > div._1u4plm2 > div:nth-child(2) > div:nth-child(2) > div > div > div > div > div._jcreqo > div._fjltwx > div > div._3zzdxk > div > div > div > div > div._1b96w9b > div:nth-child(2) > div._t0tx82 > div._8sgdp4 > div > div:nth-child(1) > div._49kxlr > div > div:nth-child(2) > div:nth-child(1)').text
        except:
            street = "error"
        try:
            descr = driver.find_element(By.CLASS_NAME,'_1p8iqzw').text
        except:
            descr = "error"

        # print(str(driver.current_url))
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

        # lat = lat_meet + str(str(driver.current_url).split(lat_meet)[1].split('%')[0].split('?')[0])

        # long = long_meet + str(str(driver.current_url).split(long_meet)[1].split('?')[0].split('%')[0])



        # print(lat, long)

        arr_lat.append(lat)
        arr_long.append(long)


        # coord = coords[1]
        geos.append(descr)
        ulitsa.append(street)
        arr_stars.append(stars)
        arr_voices.append(count_voices)
        points.append(name)






        # print(name,coord)


    actions.move_to_element(scroll_elements).perform()
    time.sleep(1)
    # actions.click().perform()
    scroll_elements.click()
    print('page= ',i)

    i += 1
    print(len(arr_lat), len(points))

    # df = pd.DataFrame({'name': points, 'coords': geos, 'ulitsa': ulitsa})
    df = pd.DataFrame({'name': points, 'descr': geos, 'ulitsa': ulitsa, 'stars': arr_stars, 'count_voices': arr_voices, 'lat' : arr_lat, 'long': arr_long})
    # df = pd.DataFrame({'name': points,  'ulitsa': ulitsa})
    df.to_csv(fr'C:\Users\sergey.biryukov\Desktop\Москва генплан конкурс\Общепит/{file_name}.csv', sep=';', encoding='utf8', index=False)

    # читаем данные из строки TSV и создаем DataFrame
    data = pd.read_csv(rf'C:\Users\sergey.biryukov\Desktop\Москва генплан конкурс\Общепит/{file_name}.csv', sep=' ; ')
    print(data)





driver.quit()
