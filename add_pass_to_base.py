import gspread
from gspread import Cell, Client, Spreadsheet, Worksheet
import datetime
import socket
import os

class BasePassParcer:
    def __init__(self):
        self.googe_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        self.all_query = 1000
        self.id_person = None
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        self.sh: Spreadsheet = gc.open_by_url(self.googe_sheet_url)
        self.ws = self.sh.sheet1
        self.ws_tarif = self.sh.worksheet('tarifs')

    def verify_computer(self,ws: Worksheet ): #если мы нажали на кнопку без авторизации
        def max_id(ws: Worksheet):
            arr_id = ws.col_values(1, value_render_option="UNFORMATTED_VALUE")[1:]
            new_id = max(arr_id) + 1
            return new_id
        def get_local_ip():
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            # print(local_ip)
            username = os.getlogin()
            return local_ip, username

        local_ip, username = get_local_ip()

        cell_1: Cell = ws.find(local_ip, in_column=3) #Ищем наш ip в списке IP
        # cell_2: Cell = ws.find(username, in_column=5)

        if cell_1 :
            row = ws.row_values(cell_1.row)
            # print(row[4],"row4")
            if row[4] == username:
                # print("такой комп есть")
                self.id_person = row[0]
                self.all_query = row[7]
                print('id = ', row[0])
                print('query = ', self.all_query)
                return row[0], row[7]
            else:
                # print("ЕСть ip, но нет  юзера")
                non_authorisation_tarif = self.get_tarif(self.ws_tarif, 'non_authorisation')
                # print(non_authorisation_tarif)
                new_id = max_id(ws)
                self.create_value(self.ws, "", "", 'non_authorisation')
                return new_id, non_authorisation_tarif
        else:
            # print("Нет такого компа")
            non_authorisation_tarif = self.get_tarif(self.ws_tarif, 'non_authorisation')
            new_id = max_id(ws)
            self.create_value(self.ws, "", "",'non_authorisation')
            return new_id, non_authorisation_tarif

    def create_value(self,ws: Worksheet, company, password, tarif = 'non_authorisation'):
        def max_id(ws: Worksheet):
            arr_id = ws.col_values(1, value_render_option="UNFORMATTED_VALUE")[1:]
            new_id = max(arr_id) + 1
            return new_id
        current_date = datetime.date.today().isoformat()
        arr = {"id": max_id(ws),
               "NAME": None,
               "LOCAL_IP": socket.gethostbyname(socket.gethostname()),
               "HOSTNAME": socket.gethostname(),
               "USERNAME": os.getlogin(),
               "COMPANY": company,
               "PASS": password,
               "COUNT": int(self.get_tarif(self.ws_tarif, tarif)),
               "TARIF": tarif,
               "ALL_COUNT": 0,
               "LAST_QUERY": current_date,
               "REGISTRY_DATE": current_date}
        ws.insert_rows([list(arr.values())],2)

    def verify_person(self,ws: Worksheet, person):
        # print("verify_person")
        cell: Cell = ws.find(person,in_column=2)
        if cell:
            # print("Такой юзер есть")
            row = ws.row_values(cell.row)
            self.id_person = row[0] #ид компьютера
            self.all_query = row[7] #подгружаем к-во запросов
            # print("id = ",row[0])
            return row[0],row[6], row[7]
        else:
            # print("Нет такого юзера")
            return None, None,None
    def get_queries(self, ws: Worksheet, id_person):
        cell: Cell = ws.find(str(id_person),in_column=1)
        if cell:
            row = ws.row_values(cell.row)
            # print(row[7])
            return row[7]

    # def set_queries(self, ws: Worksheet, id_person, value):
    #     cell: Cell = ws.find(str(id_person),in_column=1)
    #     if cell:
    #         row = cell.row
    #         ws.update_cell(row, 8, value)

    def set_queries(self, ws: Worksheet, id_person, sh: Spreadsheet, value):
        cell: Cell = ws.find(str(id_person), in_column=1)
        if cell:
            row = cell.row
            updates = [
                {
                    'updateCells': {
                        'rows': [{'values': [{'userEnteredValue': {'numberValue': value}}]}],
                        'fields': '*',
                        'range': {
                            'sheetId': ws.id,
                            'startRowIndex': row - 1,
                            'endRowIndex': row,
                            'startColumnIndex': 7,
                            'endColumnIndex': 8
                        }
                    }
                },
                {
                    'updateCells': {
                        'rows': [{'values': [{'userEnteredValue': {'stringValue': datetime.date.today().isoformat()}}]}],
                        'fields': '*',
                        'range': {
                            'sheetId': ws.id,
                            'startRowIndex': row - 1,
                            'endRowIndex': row,
                            'startColumnIndex': 10,
                            'endColumnIndex': 11
                        }
                    }
                }
            ]

            # Форматирование тела запроса
            body = {'requests': updates}

            # Выполнение batch_update
            sh.batch_update(body)



    def get_tarif(self, ws: Worksheet,tarif):
        cell: Cell = ws.find(tarif, in_column=1)
        if cell:
            row = ws.row_values(cell.row)
            name_tarif = row[0]
            query_tarif = row[1]
            # print(query_tarif)
            # print(name_tarif)
            return query_tarif
        else:
            print("Нет такого Тарифа")
            return None

    def main(self):
        # gc: Client = gspread.service_account("./etc/google_service_account.json")
        # self.sh: Spreadsheet = gc.open_by_url(self.googe_sheet_url)
        # ws = self.sh.sheet1
        # self.ws_tarif = self.sh.worksheet('tarifs')
        # self.verify_computer(ws)
        self.set_queries2(self.ws,9,self.sh,400)
        # self.get_tarif(self.ws_tarif, "non_autorisation")








if __name__ == '__main__':
    obj = BasePassParcer()
    obj.main()