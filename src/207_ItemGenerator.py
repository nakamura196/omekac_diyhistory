import sys
import urllib
import json
import argparse
import requests
import os
import shutil
import yaml

f = open("settings.yml", "r+")
settings = yaml.load(f)

dir = "../docs/api/items"
if os.path.exists(dir):
    shutil.rmtree(dir)
os.makedirs(dir, exist_ok=True)

api_url = settings["api_url"]
key = settings["key"]
mod = ""

def base_generator():

    loop_flg = True
    page = 1

    while loop_flg:
        url = api_url + "/items?page=" + str(
            page)
        print(url)

        page += 1

        if key != "":
            url += "&key="+key

        if mod != "":
            url += "&modified_since="+mod

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
