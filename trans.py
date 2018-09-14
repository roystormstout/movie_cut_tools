#!/usr/bin/python

import sys
import json
from googletrans import Translator

with open(sys.argv[1], "r") as f:
    data = json.load(f)


translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.com.hk',
    ])

synops = data['synopsis'].split('\t')
title = data['title']
storyline = data['story_line']
synops_cn = ""

for s in synops:
    synops_cn = synops_cn + translator.translate(s, dest='zh-cn').text + "\t"
    # print(translator.translate(s, dest='zh-cn').text)

print(synops_cn)
synops_cn = synops_cn[:-1]
title_cn = translator.translate(title, dest='zh-cn').text
data['title_cn'] = title_cn
storyline_cn = translator.translate(storyline, dest='zh-cn').text
data['story_line_cn'] = storyline_cn
data['synopsis_cn'] = synops_cn


with open(sys.argv[1], "w") as jsonFile:
    json.dump(data, jsonFile)

