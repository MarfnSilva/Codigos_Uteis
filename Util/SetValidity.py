# -*- coding: utf-8 # -*- 

#from GET_teste import User
#from typing import no_type_check
#from GenericTrace import trace
import requests, json, traceback, sys, base64, re, os
from datetime import datetime  
#import datetime
#from dateutil.relativedelta import relativedelta
from datetime import timedelta  
from requests.models import Response
import time
#from WXSConnection import *


waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'ValidadeASO:#TesteAPI01#', 'WAccessUtcOffset': '-180'}
user_chid = sys.argv[1]
user_chtype = sys.argv[2]
#user_chid = 4018
#user_chtype = '5'

if user_chtype in ('2', '3'):
    get_user1 = requests.get(waccessapi_endpoint + f'cardholders/' + str(user_chid), headers=waccessapi_header, params=(("CHType", user_chtype),("limit", '20000')))
    get_user_json1 = get_user1.json()
    get_dif= get_user_json1 # + get_user_json2

    if get_dif["AuxDte04"] and get_dif["AuxChk02"] == 0:
        valdidade_str = get_dif["AuxDte04"]
        validade_date = datetime.strptime(valdidade_str, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=3)
        get_dif["CHEndValidityDateTime"] = validade_date.strftime("%Y-%m-%dT%H:%M:%S")
        requests.put(waccessapi_endpoint + f'cardholders', json=get_dif, headers=waccessapi_header, params=(("callAction", False),))
        #print(f'O Usuário de CHID: {get_dif["CHID"]} - Teve a Validade alterada para {get_dif["CHEndValidityDateTime"]}')


