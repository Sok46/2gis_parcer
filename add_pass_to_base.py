
import gspread
from gspread import Cell, Client, Spreadsheet, Worksheet
import  datetime

class BasePassParcer:
    def __init__(self):
        self.googe_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'

    def my_method(self):
        print(111)
    def show_worksheets(self,sh: Spreadsheet):
        worksheets = sh.worksheets()
        for ws in worksheets:
            print(ws)

    def create_value(self,ws: Worksheet, arr):
        ws.insert_rows([list(arr.values())],2)

    def verify_person(self,ws: Worksheet, person):

        cell: Cell = ws.find(person,in_column=2)

        row = ws.row_values(cell.row)
        print(row[3])
        return row[3]


    def max_id(self,ws: Worksheet):
        arr_id = ws.col_values(1, value_render_option="UNFORMATTED_VALUE")[1:]
        new_id = max(arr_id) + 1
        return new_id


    def main(self):
        gc: Client = gspread.service_account("./etc/google_service_account.json")
        sh: Spreadsheet = gc.open_by_url(self.googe_sheet_url)
        ws = sh.sheet1
        current_date = datetime.date.today().isoformat()
        # arr = [0,"biba", "pass228", 5000,0, current_date]
        arr = {"id": self.max_id(ws) ,
                "NAME":"biba2",
                "COMPANY":"bibaboss",
                "PASS":"pass228",
                "COUNT":5000,
                "ALL_COUNT":1,
                "LAST_QUERY": current_date,
                "REGISTRY_DATE": current_date}
        print(sh)

        self.show_worksheets(sh)
        # self.max_id(ws)
        # self.create_value(ws, arr)
        self.verify_person(ws, "yulia")




if __name__ == '__main__':
    obj = BasePassParcer()
    obj.main()