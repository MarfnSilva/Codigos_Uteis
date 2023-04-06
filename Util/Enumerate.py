# -*- coding: utf-8 # -*- 

from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests, json, traceback, sys, base64, re
from GenericTrace import report_exception, trace

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

user = requests.get(waccessapi_endpoint + f'cardholders', headers=waccessapi_header, params=(("CHType", 5),("limit", '20000')))
get_user  = user.json()

for i, wxs_user in enumerate(get_user):
    print(f'{i} - {wxs_user["FirstName"]}')