import requests

url = "http://172.16.17.75/frapi/people"

headers = {
    'content-type': "application/json",
    'app_key': "43d26218da4a48c7aa6c7d2ef9e4042f"
    }

response = requests.request("GET", url, headers=headers)
response_json = response.json()
lista = response_json['people']
i = 0
for user in lista:
    response = requests.request("DELETE", url + f'/{user["person_label"]}', headers=headers)
    print(f'{i} - {response.text}')





