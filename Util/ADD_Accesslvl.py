# -*- coding: utf-8 # -*- 

from requests.models import Response
from datetime import *
import time
from datetime import timedelta 
import requests#, json, traceback, sys, base64, re
# from GenericTrace import report_exception, trace

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

user = requests.get(waccessapi_endpoint + f'cardholders', headers=waccessapi_header, params=(("CHType", 2),("limit", '20000')))
get_user  = user.json()

for i, wxs_user in enumerate(get_user):
    #teste = wxs_user["CHID"] + 200000000
    
    # if  wxs_user["CompanyID"] in (3, 4):
    assign = requests.post(waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/accessLevels/2', headers=waccessapi_header, json={}, params=(("callAction", False),))
    print(f'{i} - CHID {wxs_user["CHID"]} - OK')
    time.sleep(0.3)
    

