# -*- coding: utf-8 # -*- 

from datetime import *
from datetime import timedelta 
import requests,sys
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

# user_chtype = 2

try:

    get_user1 = requests.get(url + f'cardholders/', headers=h, params=(("CHType", 2),("includeTables", "Cards"),("limit", '20000')))
    get_users = get_user1.json()

    trace('----------Início da Interação---------')

    for wxs_user in get_users:

        # Valida se o usuário tem Data de Férias e Período preenchidos
        if wxs_user["AuxDte10"] and wxs_user["AuxLst15"] != -1:

            # Rotina para usuários com mais de 1 cartão
            card_lst = []
            for card in wxs_user["Cards"]:
                card_lst.append(card)

            index = wxs_user["AuxLst15"] if wxs_user["AuxLst15"] != None else 0

            get_user2 = requests.get(url + f'chComboFields?chType=2&fieldID=lstBDA_AuxLst15&comboIndex={index}' , headers=h)
            wxs_user_lst = get_user2.json()

            get_user3 = requests.get(url + f'cardholders/' + str(wxs_user["CHID"]) + '/lastTransit', headers=h)
            wxs_user_zone = get_user3.json()

            zone_id = int(wxs_user_zone["ZoneID"]) if wxs_user_zone else 0

            for combo in wxs_user_lst:
                dias = int(combo["strLanguage2"])

            # Formata o período de férias
            valdidade_str = wxs_user["AuxDte10"]
            date_ignore = datetime.strptime(valdidade_str, "%Y-%m-%dT%H:%M:%S")
            ferias = datetime.strptime(valdidade_str, "%Y-%m-%dT%H:%M:%S") + timedelta(dias) 
            now_date = datetime.now()

            # Ignora usuário se a data de início de férias for maior que a data atual
            if date_ignore > now_date:
                continue
            
            # Fluxo para usuários COM férias vigentes
            if ferias >= now_date:

                # Valida se o usuário já está com CHState "Férias"
                if wxs_user["CHState"] in (3, 4):
                    trace(f'CHID:{wxs_user["CHID"]} - {wxs_user["FirstName"]} - Permanece de Férias - {wxs_user["AuxDte10"]} + {dias} dias')
                else:

                    # Valida se o usuário esta na zona externa antes de mudar o CHState
                    # if zone_id == 3:
                        wxs_user["CHState"] = 3 if wxs_user["AuxChk02"] == False else 4
                        trace(f'CHID:{wxs_user["CHID"]} - {wxs_user["FirstName"]} - Iniciou as Férias - {wxs_user["AuxDte10"]} + {dias} dias')
                        update_user = requests.put(url + f'cardholders', json=wxs_user, headers=h, params=(("callAction", False),))
                    # else:
                    #    trace(f'CHID:{wxs_user["CHID"]} - {wxs_user["FirstName"]} - Não está na Zona Externa') 
            
            else:

                # Fluxo para usuários SEM férias vigentes
                if wxs_user["CHState"] in (3, 4):
                    trace(f'CHID:{wxs_user["CHID"]} - {wxs_user["FirstName"]} - Voltou de Férias - {wxs_user["AuxDte10"]} + {dias} dias')
                    wxs_user["CHState"] = 0
                    wxs_user["AuxDte10"] = None
                    wxs_user["AuxLst15"] = None
                    wxs_user["AuxChk02"] = False
                    update_user = requests.put(url + f'cardholders', json=wxs_user, headers=h, params=(("callAction", False),))
                    if card_lst:

                        # Percorre a lista de cartões para ativar todos os cartões do usuário
                        for card in card_lst:
                            card["CardState"] = 0
                            teste = requests.post(url + f'cardholders/{wxs_user["CHID"]}/cards', json=card, headers=h, params=(("callAction", False),))

                else:
                    continue

        else:
            continue
            
    trace('------------Fim da Interação----------')

except Exception as ex:
    report_exception(ex)



