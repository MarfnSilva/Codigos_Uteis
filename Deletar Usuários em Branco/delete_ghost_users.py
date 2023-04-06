# -*- coding: utf-8 # -*- 

from datetime import *
from datetime import timedelta 
import requests, pyodbc
#from unidecode import unidecode
from GenericTrace import report_exception, trace
import configparser

parser = configparser.ConfigParser()
parser.read("Config.cfg")
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

try:

    conn = pyodbc.connect('Driver='+odbcdriver+';Server='+servername+';UID='+userid+';PWD='+password+';Database='+databasename) 
    cursor = conn.cursor()

    script = f"SELECT CHID FROM CHMain WHERE FirstName = '' "
    cursor.execute(script)

    for sql_row in cursor:
        list_chid.append(sql_row[0])

    for i, chid in enumerate(list_chid):
        script = f"SELECT CHCategory FROM CHMain JOIN CfgCHTypes ON CfgCHTypes.CHType = CHMain.CHType WHERE CHID = {chid} "
        cursor.execute(script)

        for sql_row in cursor:
            tipo = int(sql_row[0])
        
        if tipo == 1:
            delvisit = requests.delete(url + f'cardholders/{chid}/activeVisit', headers=h, params=(("callAction", False),))

        del_user = requests.delete(url + f'cardholders/{chid}', headers=h)
        if del_user.status_code == requests.codes.no_content:
            print(f'{i} - CHID {chid} - Deletado com Sucesso')

        else:
            print(f'{i} - CHID {chid} - {del_user.json()["Message"]}')

except Exception as ex:
    report_exception(ex)

    
