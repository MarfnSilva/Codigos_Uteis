# -*- coding: utf-8 # -*- 

# from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests#, json, traceback, sys, base64, re
import time

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

#user_chid = 669
n = 0

user = requests.get(waccessapi_endpoint + f'cardholders', headers=waccessapi_header, params=(("CHType", (1, 2)),("limit", '20000')))
get_user  = user.json()

#while True:
for wxs_user in get_user:
    # teste = 1
    # wxs_user["AuxText09"] = teste
    wxs_user["FirstName"] =  wxs_user["FirstName"].upper()
    #wxs_user["IdNumber"] = wxs_user["IdNumber"].replace(" ", "")
    update_user = requests.put(waccessapi_endpoint + f'cardholders', json=wxs_user, headers=waccessapi_header, params=(("callAction", False),))
    
    print(update_user)
    n += 1
    print(f'{n} - Usuário {wxs_user["FirstName"]} foi atualizado!')
    time.sleep(0.3)
teste =+ 1

#print(nome,doc)