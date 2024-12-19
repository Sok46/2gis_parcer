
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
                    and "plain" in log_["params"]["response"]["mimeType"] #Нужно посмотреть mimetype хар файла и какой там mimetype у фичей
            )

        def merge_geojson(logi):
            merged_features = []

            for log in logi:
                try:
                    # Преобразуем строку JSON в объект Python, если это нужно
                    geojson_obj = json.loads(log["body"])  # log["body"] — это содержимое geoJSON
                    features = geojson_obj.get("features", [])
                    merged_features.extend(features)  # Добавляем все features
                except Exception as e:
                    print(f"Ошибка обработки логов: {e}")

            # Итоговый объединенный GeoJSON
            merged_geojson = {
                "type": "FeatureCollection",
                "features": merged_features
            }

            return merged_geojson


        for log in filter(log_filter, logs):
            try:
                request_id = log["params"]["requestId"]
                # resp_url = log["params"]["response"]["url"]
                # resp_qq = log["params"]["response"]

                # print(f"Caught {resp_url}", '\n stop \n')
                # print('\n start driver \n ',driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}), '\n end driver \n')
                l = (driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}))
                geojson_obj = json.loads(l["body"])  # log["body"] — это содержимое geoJSON
                features = geojson_obj.get("features", [])
                logi.extend(features)
                # print(l)
                # logi.append(l)
            except:
                pass
            merged_geojson = {
                "type": "FeatureCollection",
                "features": logi
            }

        return merged_geojson

