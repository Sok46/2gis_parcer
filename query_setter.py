

import os

class QuerySetter():
    # def __init__(self, count_queries, new_value_query,header_label):
    #     print("init")

    def check_query(self,count_queries, new_value_query,header_label):
        if count_queries < new_value_query:
            # print("Недостаточно запросов")
            header_label.setText(f"Недостаточно запросов")

            header_label.setStyleSheet("color: red;")
            return False
        else:
            return True


    #     self.set_query(count_queries, my_base, header_label, new_value_query, ws, id_person, sh)

    def set_query(self,count_queries, my_base, header_label, new_value_query, ws, id_person, sh):
        print("count_queries", count_queries)
        # print("my_base",my_base)
        # print("header_label",header_label)
        # print("new_value_query",new_value_query)
        # print("ws",ws)
        # print("id_person",id_person)
        # print("sh",sh)
        count_queries -= new_value_query
        # print("new_value_query")
        my_base.set_queries(ws, int(id_person), sh, int(count_queries))
        header_label.setText(f"У вас {count_queries} запросов")
        coinIcon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "coin.png")
        header_label.setText(f'У вас {count_queries} <img src={coinIcon_path} width="30" height="30" style="vertical-align: top;">')
        # print("new_count_queries", count_queries)
        return count_queries
