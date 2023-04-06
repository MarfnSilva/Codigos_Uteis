# -*- coding: utf-8 # -*- 

from hamcrest import contains
from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests,sys, pyodbc
from unidecode import unidecode
from GenericTrace import report_exception, trace
import configparser

parser = configparser.ConfigParser()
parser.read("Import.cfg")
servername = parser.get("config", "servername")
userid = parser.get("config", "userid")
password = parser.get("config", "password")
databasename = parser.get("config", "databasename")
odbcdriver = parser.get("config", "odbcdriver")
diretorio = parser.get("config", "diretorio")
api_server_name = parser.get("config", "api_server_name")
api_user = parser.get("config", "api_user")
api_password = parser.get("config", "api_password")

url = f'http://{api_server_name}/W-AccessAPI/v1/'
h = { 'WAccessAuthentication': f'{api_user}:{api_password}', 'WAccessUtcOffset': '-180'}

lst_func = []
lst_terc = []

conn = pyodbc.connect('Driver='+odbcdriver+';Server='+servername+';UID='+userid+';PWD='+password+';Database='+databasename) 
cursor = conn.cursor()
conn.autocommit = True

script_func = f"SELECT \
                CHLastTransit.CHID\
                FROM CHLastTransit\
                LEFT JOIN CHMain on CHMain.CHID = CHLastTransit.CHID\
                LEFT JOIN CHAux ON  CHAux.CHID = CHLastTransit.CHID\
                WHERE EventDateTime <= DATEADD(DAY, -180, GETDATE()) and CHType = 2 AND AuxLst01 <> 2"
cursor.execute(script_func)
for sql_row in cursor:
    lst_func.append(sql_row[0])

script_func = f"SELECT \
                CHLastTransit.CHID\
                FROM CHLastTransit\
                LEFT JOIN CHMain on CHMain.CHID = CHLastTransit.CHID\
                LEFT JOIN CHAux ON  CHAux.CHID = CHLastTransit.CHID\
                WHERE EventDateTime <= DATEADD(DAY, -90, GETDATE()) and CHType = 2 AND AuxLst01 = 2"
cursor.execute(script_func)
for sql_row in cursor:
    lst_terc.append(sql_row[0])

lst_chid = lst_func + lst_terc

for chid in lst_chid:
    user = requests.get(url + f'cardholders/' + str(chid), headers=h, params=(("CHType", 2),))
    wxs_user  = user.json()

    wxs_user["CHState"] = 1
    wxs_user["AuxTextA01"] = 'Desativado por Inatividade!'
    update_user = requests.put(url + f'cardholders', json=wxs_user, headers=h, params=(("callAction", False),))


