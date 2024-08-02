
import gspread
from gspread import Client, Spreadsheet, Worksheet
# from etc import service_google_account

#Запись в гугл таблицу
googe_sheet_url = 'https://docs.google.com/spreadsheets/d/1qsd5c5wDWo6YlGu-5SX-Ga8G7E-8XaE20KgMAVDYMD4/edit?gid=0#gid=0'

# def main():
#
#
def show_worksheets(sh: Spreadsheet):
    worksheets = sh.worksheets()
    for ws in worksheets:
        print(ws)

def create_value(ws: Worksheet, arr):
    ws.insert_rows([arr],2)

def show_json(ws: Worksheet):
    list_of_dicts = ws.get_all_records()
    print(list_of_dicts[0])


def main():
    gc: Client = gspread.service_account("./etc/google_service_account.json")
    sh: Spreadsheet = gc.open_by_url(googe_sheet_url)
    ws = sh.sheet1
    arr = ["f","b", "c"]
    print(sh)
    show_worksheets(sh)
    create_value(ws, arr)
    show_json(ws)
    # ws = sh.sheet1
    # ws3 = sh.get_worksheet(2)
    # paste_fields(ws)
    # wish_list_import(ws3)



if __name__ == '__main__':
    # parce()
    main()