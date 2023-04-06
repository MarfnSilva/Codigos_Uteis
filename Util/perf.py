# -*- coding: utf-8 -*-

import requests, json, sys

url = "http://localhost/W-AccessAPI/v1/"
h = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180' }


current_set = set()

while True:
    print('********* novo Iteração')
    reply = requests.get(url + 'cardholders', headers=h, params = (("CHType", '2'),("limit", '20000')))
    wxs_users_list = reply.json()
    # print(type(wxs_users_list_old))
    new_set = set()
    for wxs_user in wxs_users_list:
        user_hash = hash(json.dumps(wxs_user))
        new_set.add(user_hash)
        if not user_hash in current_set:
            # trata a alteração/inserção do wxs_user
            print(wxs_user["FirstName"])
            pass
        else:
            print('usuário não foi alterado')
    current_set = new_set