import requests

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





