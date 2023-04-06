# -*- coding: utf-8 # -*- 

from GenericTrace import report_exception, trace
import requests, json,csv#,base64
from datetime import datetime, timedelta   
import time
import pyodbc

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
url = 'http://localhost/W-AccessAPI/v1/'
h = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

# user_chid = 4545
# n = 0

user = requests.get(url + f'cardholders', headers=h, params=(("CHType", 2),("limit", '20000')))
wxs_user_list  = user.json()

# user = requests.get(url + f'cardholders/' + str(user_chid), headers=h, params=(("CHType", 2),("limit", '20000')))
# wxs_user  = user.json()


for i, wxs_user in enumerate(wxs_user_list):
    print(f'{i} - Processado')
    if wxs_user["IdNumber"]:
        if len(wxs_user["IdNumber"]) == 11:
            print('CPF')
        else:
            print('Outro')
            wxs_user["AuxText01"] = wxs_user["IdNumber"]
            wxs_user["IdNumber"] = ''
            # print(f'Aqui {wxs_user["IdNumber"]}')
            update_user = requests.put(url + f'cardholders', json=wxs_user, headers=h, params=(("callAction", False),))
        