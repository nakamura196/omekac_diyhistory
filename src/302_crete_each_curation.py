import sys
import urllib
import json
import argparse
import requests
import os
import shutil
import yaml
import glob

f = open("settings.yml", "r+")
settings = yaml.load(f)

prefix = settings["pages"]

dir = "../docs/api/items"

files = glob.glob(dir+"/*.json")

members = {}
selections = {}
manifests = []

import re

map = {}

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

for file in files:

    with open(file) as f:
        item = json.load(f)

    metadata = {}
    element_texts = item["element_texts"]

    for e in element_texts:
        metadata[e["element"]["name"]] = e["text"]

    if item["item_type"] and item["item_type"]["name"] == "Annotation":
        region = metadata["Annotated Region"]

        if "Text" not in metadata:
            # print("error", file)
            print("https://diyhistory.org/public/omekac/admin/items/show/"+file.split("/")[-1].split(".")[0])
            continue

        value = metadata["Text"]
        canvas_uuid = metadata["On Canvas"]

        if canvas_uuid not in members:
            members[canvas_uuid] = []

        members[canvas_uuid].append({
            "xywh" : region,
            "label" : value
        })

    else:
        canvas_uuid = metadata["UUID"]
        canvas_id = metadata["Original @id"]

        if canvas_id not in selections:
            selections[canvas_id] = []
        selections[canvas_id].append(canvas_uuid)

        manifest = metadata["Source"]

        if manifest not in manifests:
            manifests.append(manifest)

import hashlib

for i in range(len(manifests)):
    selections_new = []

    manifest = manifests[len(manifests) - i - 1]    

    hash = hashlib.md5(manifest.encode('utf-8')).hexdigest()

    path = "data/"+hash+".json"

    if not os.path.exists(path):

        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True)

        df = requests.get(manifest).json()

        with open(path, 'w') as outfile:
            json.dump(df, outfile, ensure_ascii=False,
                        indent=4, sort_keys=True, separators=(',', ': '))

    with open(path) as f:
        m = json.load(f)

    if "sequences" not in m:
        print("KeyError: 'sequences'", manifest)
        continue

    label = m["label"]
    print(i+1, len(manifests), label, hash)
    
    if label in map:
        print("label", "dupppp")
    map[label] = hash

    canvases = m["sequences"][0]["canvases"]

    members_new = []

    for canvas in canvases:
        canvas_id = canvas["@id"]

        if canvas_id in selections:

            uuids = selections[canvas_id]

            for canvas_uuid in uuids:

                if canvas_uuid not in members: # ちょっとなぞ
                    continue
                
                members_ = members[canvas_uuid]

                for member in members_:
                    member_ = {
                        "@id" : canvas_id+"#xywh="+member["xywh"],
                        "label" : cleanhtml(member["label"]),
                        "@type": "sc:Canvas"
                    }

                    members_new.append(member_)

    if len(members_new) > 0:
        selection = {
            "@id": manifest+"/range",
            "@type": "sc:Range",
            "label":  m["label"],
            "members" : members_new,
            "within" : {
                "@id" : manifest,
                "@type": "sc:Manifest",
                "label" : m["label"]
            }
        }
        selections_new.append(selection)

    curation = {
        "@context": [
            "http://iiif.io/api/presentation/2/context.json",
            "http://codh.rois.ac.jp/iiif/curation/1/context.json"
        ],
        "@type": "cr:Curation",
        "@id" : prefix + "/iiif/curation/"+hash+"/curation.json",
        "label" : "琉球国絵図プロジェクト",
        "selections" : selections_new
    }

    opath = "../docs/iiif/curation/"+hash+"/curation.json"
    dirname = os.path.dirname(opath)
    os.makedirs(dirname, exist_ok=True)

    with open(opath, 'w') as outfile:
        json.dump(curation, outfile, ensure_ascii=False,
                    indent=4, sort_keys=True, separators=(',', ': '))


print(map)