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

#Servidor Palacio - 'NORION-31741\W_ACCESS' 

user_chid = int(sys.argv[1])
user_auxlist = int(sys.argv[2])
user_chtype = int(sys.argv[3])

# user_chid = 5552
# user_auxlist = 5
# user_chtype = 2

try:

    if user_chtype == 2:
        
        lvl_id = []

        ac = requests.get(url + f'accessLevels', headers=h)
        all_access_levels = ac.json()

        user = requests.get(url + f'cardholders/' + str(user_chid), headers=h, params=(("CHType", 2),("includeTables","CHAccessLevels")))
        wxs_user  = user.json()

        conn = pyodbc.connect('Driver='+odbcdriver+';Server='+servername+';UID='+userid+';PWD='+password+';Database='+databasename) 
        cursor = conn.cursor()

        # Consulta os nomes da lista AuxLst01
        script_combo = f"SELECT strLanguage2 FROM CfgCHComboFields WHERE fieldid = 'lstBDA_AuxLst01' AND CHType = 2 AND ComboIndex = {user_auxlist}"
        cursor.execute(script_combo)
        for sql_row in cursor:
            access_level_name = sql_row[0]

        # Consulta todos os níveis de acesso com o prefixo 'Padrão' e add na lista 'lvl_id' criada para remoção
        script_lst = f"SELECT AccessLevelID FROM CfgACAccessLevels WHERE AccessLevelName LIKE 'Padrão%'"
        cursor.execute(script_lst)
        for sql_row in cursor:
            lvl_id.append(sql_row[0])

        # Consulta o nível id do nível de acesso contido na lista 'AuxLst01' para tira-lo do loop de remoção
        script_lst = f"SELECT AccessLevelID FROM CfgACAccessLevels WHERE AccessLevelName LIKE '%{access_level_name}%'"
        cursor.execute(script_lst)
        for sql_row in cursor:
            print(sql_row[0])
            lvl_id.remove(sql_row[0])

        for access_level in all_access_levels:
            # Procura o nível de acesso usando o nome contido no AuxLst01 e desconsiderando o prefixo do nome no nível de acesso
            if access_level["AccessLevelName"].upper().rfind(access_level_name.upper()) != -1:
                
                ignore = 0
                for name in wxs_user["CHAccessLevels"]:
                    # Valida se o usuário já possui o nível de acesso para não "sujar" a auditoria
                    if access_level["AccessLevelID"] == name["AccessLevelID"]:
                        print(f'Usuário já possui o nível de acesso {access_level["AccessLevelName"]}')
                        ignore = 1
                        continue

                # Add nível de acesso
                if ignore == 0:
                    trace(f'Nivel de acesso Assossiado com AccessLevelID = {access_level["AccessLevelID"]} e AccessLevelName = {access_level["AccessLevelName"]}')
                    assign = requests.post(url + f'cardholders/{user_chid}/accessLevels/{access_level["AccessLevelID"]}', headers=h, json={}, params=(("callAction", False),))

            else:
                for delete in wxs_user["CHAccessLevels"]:
                    # Remove nível de acesso do usuário que estiver na lista 'lvl_id'
                    if delete["AccessLevelID"] in lvl_id:
                        del_access_level = requests.delete(url + f'cardholders/{user_chid}/accessLevels/{delete["AccessLevelID"]}', headers=h)
                        lvl_id.remove(delete["AccessLevelID"])

        # Valida se o dia é par ou ímpar
        numero = int(datetime.now().strftime("%d"))
        if (numero%2) == 0:

            trace("Rotina Dia Par")
            script = f"SELECT * FROM CHGroups WHERE GroupID IN (77, 78, 93, 94, 109, 110, 123, 124, 130, 131) AND CHID = {user_chid}" #lvl_id.append(sql_row[0])
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

            trace("Rotina Dia Ímpar")
            script = f"SELECT * FROM CHGroups WHERE GroupID IN (77, 78, 93, 94, 109, 110, 123, 124, 130, 131) AND CHID = {user_chid}"
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

    else:
        sys.exit(0)

except Exception as ex:
    report_exception(ex)


