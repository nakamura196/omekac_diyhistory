import sys
import urllib
import json
import argparse
import requests
import os
import shutil
import glob

prefix_1 = "https://diyhistory.org/public/omekac"
prefix_2 = "../../docs"
prefix_3 = "https://raw.githubusercontent.com/nakamura196/omekac_diyhistory/master/docs"

key = "4d243dc18b79edb3fe32abf8abbaf8605453e87e"

def get(data_json, data_url):
    # data_json = requests.get(data_url).json()

    data_path = data_url.replace(prefix_1, prefix_2)

    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    with open(data_path, 'w') as outfile:
        json.dump(data_json, outfile, ensure_ascii=False,
                    indent=4, sort_keys=True, separators=(',', ': '))

files = sorted(glob.glob(prefix_2+"/api/collections/*.json"))

manifests = []

for k in range(len(files)):
    file = files[k]

    id = file.split("/")[-1].split(".")[0]

    '''
    if id != "240":
        continue
    '''
        
    manifest_url = prefix_1 + "/oa/collections/"+str(id)+"/manifest.json"
    print(manifest_url)

    try:
        manifest_json = requests.get(manifest_url).json()

        canvases = manifest_json["sequences"][0]["canvases"]

        for i in range(len(canvases)):
            canvas = canvases[i]
            
            otherContent_url = canvas["otherContent"][0]["@id"]

            anno_id = int(otherContent_url.split("/")[-2])

            print(i+1, "canvas num", len(canvases), "anno_id", anno_id, k+1, "file num", len(files))

            canvas["otherContent"][0]["@id"] = canvas["otherContent"][0]["@id"].replace(prefix_1, prefix_3)

            # --------

            
            otherContent_json = requests.get(otherContent_url).json()
            otherContent_json["@id"] = otherContent_json["@id"].replace(prefix_1, prefix_3)

            resources = otherContent_json["resources"]

            if len(resources) != 0:

                ons = resources[0]["on"]

                for on in ons:
                    on["within"]["@id"] = on["within"]["@id"].replace(prefix_1, prefix_3)

            get(otherContent_json, otherContent_url)
    

        manifest_json["@id"] = manifest_json["@id"].replace(prefix_1, prefix_3)
        get(manifest_json, manifest_url)

        manifests.append({
            "@id": manifest_json["@id"],
            "@type": "sc:Manifest",
            "label": manifest_json["label"]
        })

    except Exception as e:
        print(e)

    # --------

    


collection = {
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": prefix_3 + "/oa/top.json",
    "@type": "sc:Collection",
    "label" : "トップコレクション",
    "manifests": manifests
}

get(collection, "../../docs/oa/top.json")

