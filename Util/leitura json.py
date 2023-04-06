

import json

with open('export_file.json', 'r') as reader:
    file = json.load(reader)


print(type(file))
