
import gspread
from gspread import Cell, Client, Spreadsheet, Worksheet
import  datetime
import socket
import os

class BasePassParcer:
    def __init__(self):
        self.googe_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'
        # self.name = 'sergey'
        # self.local_ip  = '192.168.31.18'
        # self.hostname = 'doshi'
        # self.username = 'bibasos1337'
        # self.company = 'center'
        # # self.password = 'biba228'
        # self.name = name
        # self.local_ip  = local_ip
        # self.hostname = hostname
        # self.username = username
        # self.company = company
        # self.password = password

    def my_method(self):
        print(111)
    def show_worksheets(self,sh: Spreadsheet):
        worksheets = sh.worksheets()
        for ws in worksheets:
            print(ws)

    # def create_value(self,ws: Worksheet, arr):
    #     ws.insert_rows([list(arr.values())],2)
    def create_value(self,ws: Worksheet, company, password):
        def max_id(ws: Worksheet):
            arr_id = ws.col_values(1, value_render_option="UNFORMATTED_VALUE")[1:]
            new_id = max(arr_id) + 1
            return new_id
        print(228)

        current_date = datetime.date.today().isoformat()
        print(111)
        arr = {"id": max_id(ws),
               "NAME": None,
               "LOCAL_IP": socket.gethostbyname(socket.gethostname()),
               "HOSTNAME": socket.gethostname(),
               "USERNAME": os.getlogin(),
               "COMPANY": company,
               "PASS": password,
               "COUNT": 5000,
               "ALL_COUNT": 0,
               "LAST_QUERY": current_date,
               "REGISTRY_DATE": current_date}
        print(1488)

        ws.insert_rows([list(arr.values())],2)

    def verify_person(self,ws: Worksheet, person):


        cell: Cell = ws.find(person,in_column=2)
        if cell:


            row = ws.row_values(cell.row)

            print(row[3])
            return row[3]
        else:
            print("Нет такого юзера")
            return None


    def max_id(self,ws: Worksheet):
        arr_id = ws.col_values(1, value_render_option="UNFORMATTED_VALUE")[1:]
        new_id = max(arr_id) + 1
        return new_id

    def get_local_ip(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(local_ip)
        username = os.getlogin()
        print(f"Имя пользователя: {username}")


    def main(self):
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        sh: Spreadsheet = gc.open_by_url(self.googe_sheet_url)
        ws = sh.sheet1
        current_date = datetime.date.today().isoformat()
        # arr = [0,"biba", "pass228", 5000,0, current_date]
        # arr = {"id": self.max_id(ws) ,
        #         "NAME":self.name,
        #         "LOCAL_IP":self.local_ip,
        #         "HOSTNAME":self.hostname,
        #         "USERNAME":self.username,
        #         "COMPANY":self.company,
        #         "PASS":self.password,
        #         "COUNT":5000,
        #         "ALL_COUNT":0,
        #         "LAST_QUERY": current_date,
        #         "REGISTRY_DATE": current_date}
        # print(sh)


        # self.show_worksheets(sh)
        # self.max_id(ws)
        self.create_value(ws, 1,2)

        self.verify_person(ws, "hga")
        # self.create_value(ws, "hga")




if __name__ == '__main__':
    obj = BasePassParcer()
    obj.main()