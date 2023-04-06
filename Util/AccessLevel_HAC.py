# -*- coding: utf-8 # -*- 

from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests, json, traceback, sys, base64, pyodbc
from unidecode import unidecode
from GenericTrace import report_exception, trace

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

servername = 'NSP-USU-0098\W_ACCESS' # Servidor Marabras: W-ACCESS-SRV-HO\W_ACCESS 
userid = 'sa'
password = '#w_access_Adm#'
databasename = 'W_Access'
odbcdriver = '{ODBC driver 17 for SQL Server}'

user_chid = 1


ac = requests.get(waccessapi_endpoint + f'accessLevels', headers=waccessapi_header)
all_access_levels = ac.json()

user = requests.get(waccessapi_endpoint + f'cardholders/' + str(user_chid), headers=waccessapi_header, params=(("CHType", 2),("limit", '20000')))
wxs_user  = user.json()


for access_level in all_access_levels:
    if access_level["AccessLevelName"].upper() != 'TESTE':
        del_access_level = requests.delete(waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/accessLevels/{access_level["AccessLevelID"]}', headers=waccessapi_header)
    if wxs_user["AuxText08"].upper().strip() == access_level["AccessLevelName"].upper().strip():
        trace(f'Access level founded with AccessLevelID = {access_level["AccessLevelID"]} and AccessLevelName = {access_level["AccessLevelName"]}')
        assign = requests.post(waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/accessLevels/{access_level["AccessLevelID"]}', headers=waccessapi_header, json={}, params=(("callAction", False),))


