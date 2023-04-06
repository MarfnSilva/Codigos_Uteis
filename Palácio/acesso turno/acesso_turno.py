# -*- coding: utf-8 # -*-  
from datetime import *
import requests,sys, pyodbc
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

#Servidor Palacio - 'NORION-31741\W_ACCESS'

conn = pyodbc.connect('Driver='+odbcdriver+';Server='+servername+';UID='+userid+';PWD='+password+';Database='+databasename) 
cursor = conn.cursor()
conn.autocommit = True

numero = int(datetime.now().strftime("%d"))
 
if (numero%2) == 0:
    print("Rotina Dia Par")
    script = f"select * from CHGroups where GroupID in (77, 78, 93, 94, 109, 110, 123, 124, 130, 131)" #lvl_id.append(sql_row[0])
    cursor.execute(script)
    for row in cursor:
        # ADD Access LVL para o Grupo "Dias Pares"
        if row[1] == 78:
            assign = requests.post(url + f'cardholders/{row[0]}/accessLevels/62', headers=h, json={}, params=(("callAction", False),))
        if row[1] == 94:
            assign = requests.post(url + f'cardholders/{row[0]}/accessLevels/63', headers=h, json={}, params=(("callAction", False),))
        if row[1] == 110:
            assign = requests.post(url + f'cardholders/{row[0]}/accessLevels/64', headers=h, json={}, params=(("callAction", False),))
        if row[1] == 124:
            assign = requests.post(url + f'cardholders/{row[0]}/accessLevels/65', headers=h, json={}, params=(("callAction", False),))

        # Remove Access LVL do Grupo "Dias Ímpares"
        if row[1] == 77:
            del_access = requests.delete(url + f'cardholders/{row[0]}/accessLevels/62', headers=h)
        if row[1] == 93:
            del_access = requests.delete(url + f'cardholders/{row[0]}/accessLevels/63', headers=h)
        if row[1] == 109:
            del_access = requests.delete(url + f'cardholders/{row[0]}/accessLevels/64', headers=h)
        if row[1] == 123:
            del_access = requests.delete(url + f'cardholders/{row[0]}/accessLevels/65', headers=h)
        
        # Rotina para usuários do período noturno
        if row[1] == 131:
            del_access = requests.delete(url + f'cardholders/{row[0]}/accessLevels/62', headers=h)
        if row[1] == 130:
            assign = requests.post(url + f'cardholders/{row[0]}/accessLevels/62', headers=h, json={}, params=(("callAction", False),))
        
else:
    print("Rotina Dia Ímpar")
    script = f"select * from CHGroups where GroupID in (77, 78, 93, 94, 109, 110, 123, 124, 130, 131)"
    cursor.execute(script)
    for row in cursor:
        # ADD Access LVL para o Grupo "Dias Ímpares"
        if row[1] == 77:
            assign = requests.post(url + f'cardholders/{row[0]}/accessLevels/62', headers=h, json={}, params=(("callAction", False),))
        if row[1] == 93:
            assign = requests.post(url + f'cardholders/{row[0]}/accessLevels/63', headers=h, json={}, params=(("callAction", False),))
        if row[1] == 109:
            assign = requests.post(url + f'cardholders/{row[0]}/accessLevels/64', headers=h, json={}, params=(("callAction", False),))
        if row[1] == 123:
            assign = requests.post(url + f'cardholders/{row[0]}/accessLevels/65', headers=h, json={}, params=(("callAction", False),))
        
        # Remove Access LVL do Grupo "Dias Pares"
        if row[1] == 78:
            del_access = requests.delete(url + f'cardholders/{row[0]}/accessLevels/62', headers=h)
        if row[1] == 94:
            del_access = requests.delete(url + f'cardholders/{row[0]}/accessLevels/63', headers=h)
        if row[1] == 110:
            del_access = requests.delete(url + f'cardholders/{row[0]}/accessLevels/64', headers=h)
        if row[1] == 124:
            del_access = requests.delete(url + f'cardholders/{row[0]}/accessLevels/65', headers=h)
        
        # Rotina para usuários do período noturno
        if row[1] == 130:
            del_access = requests.delete(url + f'cardholders/{row[0]}/accessLevels/62', headers=h)
        if row[1] == 131:
            assign == requests.post(url + f'cardholders/{row[0]}/accessLevels/62', headers=h, json={}, params=(("callAction", False),))


