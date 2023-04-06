import requests
import json

global settings
settings = json.loads(open('settings.json').read())
'''
url = "http://10.6.119.47/frapi/people"

headers = {
    'content-type': "application/json",
    'app_key': "ea8b98f299544c1abfbf58648bee0685"
    }

response = requests.request("GET", url, headers=headers, params=(("per_page", 200000),))
response_json = response.json()
lista = response_json['people']
i = 0
for user in lista:
    response = requests.request("DELETE", url + f'/{user["person_label"]}', headers=headers)
    print(f'{i} - {response.text}')
    i += 1
'''


for ip in settings["meerket_ip_servers"]:
    meerkat_ip_server = ip["meerkat_server_ip"]
    print(f'Working with server: {meerkat_ip_server}')
    app_key = ip["appKey"]
    if not app_key:
        continue
    
    headers = {
        'content-type': "application/json",
        'app_key': app_key
        }
    try:
        print(f'Get users from server: {meerkat_ip_server}')
        response = requests.get(meerkat_ip_server + '/people', headers=headers, params=(("per_page", 200000),))
        response_json = response.json()
        lista = response_json['people']
        i = 0
        for user in lista:
            response = requests.delete(meerkat_ip_server + f'/people/{user["person_label"]}', headers=headers)
            print(f'{i} - {response.text}')
            i += 1
    except Exception as ex:
        print(ex)
