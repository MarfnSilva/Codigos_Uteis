# -*- coding: utf-8 # -*- 

from hamcrest import contains
from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests, pyodbc
from unidecode import unidecode
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

list_chid = []

conn = pyodbc.connect('Driver='+odbcdriver+';Server='+servername+';UID='+userid+';PWD='+password+';Database='+databasename) 
cursor = conn.cursor()

# Consulta os nomes da lista AuxLst01
script_combo = f"select chid from chmain where FirstName = ''"
cursor.execute(script_combo)
for sql_row in cursor:
    list_chid.append(sql_row[0])


for chid in list_chid:
    # if user["CHType"] != 1:
    del_user = requests.delete(url + f'cardholders/{chid}', headers=h)
    print(del_user.reason)