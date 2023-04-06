from typing import no_type_check
from GenericTrace import trace
import requests, json, traceback, sys, base64, re, os
from datetime import datetime  
#import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta  
from requests.models import Response
import time
from WXSConnection import *


waccess_api_server = 'localhost'
waccess_api_user = 'WAccessAPI'
waccess_api_password = '#WAccessAPI#'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'testeAPI:#testeAPI#', 'WAccessUtcOffset': '-180'}

userx = 0

get_visit = requests.get(waccessapi_endpoint + f'cardholders/searchGeneric', headers=waccessapi_header, params=(("callAction", False),("filter.startedVisits", True)))
get_visit_json = get_visit.json()
#CHID = None
for user in get_visit_json:
    delvisit = requests.delete(waccessapi_endpoint + f'cardholders/{user["CHID"]}/activeVisit', headers=waccessapi_header, params=(("callAction", False),))
    userx += 1
print(f'Visitas encerradas {userx}')