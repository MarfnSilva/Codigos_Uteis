#from GET_teste import User
from typing import no_type_check
from GenericTrace import trace
import requests, json, traceback, sys, base64, re, os
from datetime import datetime  
#import datetime
#from dateutil.relativedelta import relativedelta
from datetime import timedelta  
from requests.models import Response
import time
from WXSConnection import *


waccess_api_server = 'localhost'
#waccess_api_user = 'WAccessAPI'
#waccess_api_password = '#WAccessAPI#'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'setmaxmeal:#testeAPI#', 'WAccessUtcOffset': '-180'}
ch_access_level = {}
#cardholder_joson = {''}
tempo_inicial = time.time()

AccessLevelID = 170 # Nível de acesso Refeitório
user_count = 0

#CHType in (2, 3, 5, 6)

#get_user = requests.get(waccessapi_endpoint + f'cardholders', headers=waccessapi_header, params=(("CHType", 7),("Fields", "CHID")))
#get_user_json = get_user.json()

#get_user = requests.get(waccessapi_endpoint + f'cardholders', headers=waccessapi_header, params=(("CHType", 3),))
#get_user_json = get_user.json()

get_user1 = requests.get(waccessapi_endpoint + f'cardholders', headers=waccessapi_header, params=(("CHType", 2),("limit", '20000')))
get_user_json1 = get_user1.json()

get_user2 = requests.get(waccessapi_endpoint + f'cardholders', headers=waccessapi_header, params=(("CHType", 5),("limit", '20000')))
get_user_json2 = get_user2.json()

get_user3 = requests.get(waccessapi_endpoint + f'cardholders', headers=waccessapi_header, params=(("CHType", 6),("limit", '20000')))
get_user_json3 = get_user3.json()
print(len(get_user_json1), len(get_user_json2), len(get_user_json3))

get_dif= get_user_json1 + get_user_json2 + get_user_json3

for user in get_dif:
    if user['CHState'] == 0:
        user['MaxMeals'] = 1
        requests.post(waccessapi_endpoint + f'cardholders/{user["CHID"]}/accessLevels/{AccessLevelID}', json=ch_access_level ,headers=waccessapi_header, params=(("callAction", False),))
        requests.put(waccessapi_endpoint + f'cardholders', json=user, headers=waccessapi_header, params=(("callAction", False),))
        print(f'O Usuário de CHID:{user["CHID"]} - teve o nível de acesso adicionado ')
        user_count += 1
        time.sleep(0.3)

print(f'Usuários tratados {user_count}')
print("--- %s segundos ---" % (time.time() - tempo_inicial))