import pandas as pd
import os

folder = r'C:\Users\sergey.biryukov\Desktop\Ленинск кузнецкий\ГИС ЖКХ\Реестр'
if not os.path.exists(folder+'\export'):
    os.makedirs(folder+'\export')

for i,filename in enumerate(os.listdir(folder)):
    if filename.endswith('.csv'):
        print(filename)

        path = rf'{folder}\{filename}'



        df = pd.read_csv(path, sep = '|',encoding = 'UTF-8')


        # Удаление индекса из начала строки в колонке "address"
        # df['Адрес ОЖФ'] = df['Адрес ОЖФ'].str.slice(8)
        df.loc[df['Адрес ОЖФ'].str.contains('^\d'), 'Адрес ОЖФ'] = df['Адрес ОЖФ'].str.slice(8)
        # print(df['Адрес ОЖФ'] )

        # Город, по которому будет выполняться фильтрация
        city_filter = ' г. Полысаево'

        # Фильтрация данных по указанному городу, используя метод str.contains
        filtered_df = df[df['Адрес ОЖФ'].str.contains(city_filter, na=False)]



        # Группировка и агрегация
        result = filtered_df.groupby('Адрес ОЖФ').agg(
            # address =
            total = ('Адрес ОЖФ', 'count'),
            total_living = ('Тип помещения (блока)', lambda x: (x == 'Жилое').sum()),
            total_non_living = ('Тип помещения (блока)', lambda x: (x == 'Нежилое').sum()),
            total_living_area=('Жилая площадь в доме', 'max'),
            total_area = ('Общая площадь дома', 'max'),
            type = ('Тип дома', 'first'),
            status = ('Состояние', 'first'),
            state_host = ('Дом находится в собственности субъекта Российской Федерации и в полном объеме используется в качестве общежития', 'first'),
            substate_host = ('Дом находится в муниципальной собственности и в полном объеме используется в качестве общежития', 'first'),
            method = ('Способ управления', 'first')
        ).reset_index()


        # if len(os.listdir(folder+'\export')) == 0:
        if f'ГИС_ЖКХ_{city_filter}.csv' not in os.listdir(folder+'\export'):
            header = True

        else:
            header = False

        print(df['Адрес ОЖФ'].unique())



        result.to_csv(rf'{folder}\export\ГИС_ЖКХ_{city_filter}.csv', sep = ';',encoding = 'utf-8',header = header,mode = 'a',index=False)
    # result.to_excel(r'C:\Users\sergey.biryukov\Desktop\Ленинск кузнецкий\ГИС ЖКХ\export_data\data2.xlsx',index=False)