
import json

class filter_log:
    def logs_func(self, driver, logi, excel_df, index_features):
        print(0)

        logs_raw = driver.get_log("performance")
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

        # print(logs, '\n stop logs \n')
        print(1)

        def log_filter(log_):
            return (
                # is an actual response
                    log_["method"] == "Network.responseReceived"
                    # and json
                    and "json" in log_["params"]["response"]["mimeType"]
            )


        for log in filter(log_filter, logs):

            try:
                request_id = log["params"]["requestId"]
                # resp_url = log["params"]["response"]["url"]
                # resp_qq = log["params"]["response"]

                # print(f"Caught {resp_url}", '\n stop \n')
                # print('\n start driver \n ',driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}), '\n end driver \n')
                l = (driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}))
                logi.append(l)
            except:
                pass
        bodyes = []
        # matching_coordinates = []
        # ThreadMetaData = []
        #
        # features_list = []
        # stops = {
        #     "type": "FeatureCollection",
        #     "features": []
        # }

        # Перебираем все fetch/xhr
        for i, body in enumerate(logi):
            try:
                data = body['body']
                # if i == 1:
                json_data = json.loads((data))
                # print("\n",json_data,"\n")
                # print(f'\n ', json_data["data"]['features'], '\n')
                # print(f'\n body{i}')
                bodyes.append(json_data["data"][-1])
                # for lst in json_data['data']:
                #     print(lst, "\n")

            except:
                pass
        # geojson_data = {
        #     "type": "FeatureCollection",
        #     "features": []
        # }

        matching_prop = []
        matching_coordinates = []
        id_obj = []
        name_obj = []
        # print(bodyes)
        for last_body_item in bodyes:
            try:
                # if last_body_item['data']['features']:
                # print(last_body_item['data'])
                many_features = last_body_item['data']['features']
                for feature in many_features:
                    # feature = features.split("RenderedGeometry")
                    properties = feature['properties']
                    prop = properties["hintContent"]
                    g_obj = properties['geoObject']['geometry']
                    id = properties['geoObject']['id']
                    if "(" in prop:
                        name = prop.split("(")[0]
                        prop = prop.split("(")[1]

                        # prop = excel_df.loc[excel_df['prop'] == prop, 'new_name'].values
                    else:
                        name = "-"
                    # Пример использования объединенных данных
                    for index, row in excel_df.iterrows():
                        prop_xlsx = row['prop']
                        new_xlsx = row['new_name']
                        if prop_xlsx in prop:
                            prop = prop.replace(prop, new_xlsx)
                    # print("prop:",prop_match)

                    id_obj.append(id)
                    name_obj.append(name)
                    matching_prop.append(prop)
                    matching_coordinates.append(g_obj)

                    # print("\n", "g_obj:",g_obj, "\n")

                # print("\n", route_features, "\n")
            except:
                pass
        # print()

        if len(id_obj) != 0:
            # print("id_obj",id_obj)
        #     index_features.append(0)
        # else:
            index_features.append(set(id_obj))

        features = []
        for i in range(len(matching_coordinates)):
            feature = {
                "type": "Feature",
                # "properties:"
                "id": id_obj[i],
                "name": name_obj[i],
                "category": matching_prop[i],

                "geometry": matching_coordinates[i]
            }
            # unique_feature =  dict.fromkeys(feature).keys()
            features.append(feature)
            # index_features.append(len(features))
        # print("features:",features)
        # clear_features = list(set(map(str, features)))

        # print("clear:", features)

        geojson_data = {
            "type": "FeatureCollection",
            # "crs": {
            #     "type": "name",
            #     "properties": {
            #         "name": "urn:ogc:def:crs:EPSG::3395"
            #     }
            # },
            "features": features
        }
        # geojson_str = json.dumps(geojson_data)
        # print(geojson_data)
        # print("fin")
        return geojson_data

