import sys
import urllib
import json
import argparse
import requests
import os
import shutil
import yaml

dir = "../../docs/api/collections"
if os.path.exists(dir):
    shutil.rmtree(dir)
os.makedirs(dir, exist_ok=True)

def base_generator():
    api_url = "https://diyhistory.org/public/omekac/api"

    loop_flg = True
    page = 1

    while loop_flg:
        url = api_url + "/collections?page=" + str(
            page)
        print(url)

        page += 1

        headers = {"content-type": "application/json"}
        r = requests.get(url, headers=headers)
        data = r.json()

        if len(data) > 0:
            for i in range(len(data)):
                obj = data[i]

                id = str(obj["id"])
                # if settings["identifier"] in obj:
                #     id = obj[settings["identifier"]][0]["@value"]

                uri = api_url + "/" + id + ".json"

                obj["@id"] = uri

                with open(dir+"/"+id+".json", 'w') as outfile:
                    json.dump(obj, outfile, ensure_ascii=False,
                              indent=4, sort_keys=True, separators=(',', ': '))

        else:
            loop_flg = False


if __name__ == "__main__":

    base_generator()
