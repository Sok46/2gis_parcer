import pandas as pd
import requests
from urllib.parse import urlencode
import yadisk
tkn = "y0_AgAAAAAGvkyVAAyD3AAAAAESV2AkAABx7BX4XRNEv7zh0HWaFEzZX1T2nA"
y = yadisk.YaDisk(token=tkn)
gis_folder = "/ГИС ЖКХ/Сведения_об_объектах_жилищного_фонда_на_15-09-2024"
regions = []
for item in y.listdir(gis_folder):
    file = f"path: {item['path']}"
    region = file.split('Сведения по ОЖФ ')[1].split(' на ')[0]
    regions.append(region)
print(set(regions))

for item in y.listdir(gis_folder):
    # item.publish()

    print(f"Название: {item['name']}")
    # print(f"path: {item['path']}")
    # print(f"public_url: {item['public_url']}")

    # используем api
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = item['public_url']

    # получаем url
    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']
    # print(download_url)

    # загружаем файл в df
    download_response = requests.get(download_url)
    df = pd.read_csv(download_url, sep='\t')
    print(df)

    #
    # print(f'Размер: {item["size"]} байт')
    # print(f"Тип файла: {item['type']}")
    # print(f"Тип документа: {item['media_type']}")
    print(f"Дата создания: {item['created']}\n")




