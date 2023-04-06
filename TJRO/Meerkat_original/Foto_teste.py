import requests, json, traceback, sys, base64, re, os
from datetime import datetime  
from datetime import timedelta  
from requests.models import Response
import time


waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}



get_user = requests.get(waccessapi_endpoint + f'cardholders/7/photos/1', headers=waccessapi_header)
get_user_json = get_user.json()
print(get_user_json)