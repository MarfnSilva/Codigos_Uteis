# -*- coding: utf-8 # -*- 

from GenericTrace import report_exception, trace
import requests, json, traceback, sys, re, os, csv#,base64
from datetime import datetime  
from datetime import timedelta  
from requests.models import Response
import time
#from WXSConnection import *

waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'ValidadeASO:#TesteAPI01#', 'WAccessUtcOffset': '-180'}


def create_card(new_card, user_list):
    print(f'Creating new card.')
    create_card = requests.post(waccessapi_endpoint + f'cards', json=new_card)
    card = create_card.json()
    requests.post(waccessapi_endpoint + f'cardholders/{user_list["CHID"]}/cards', json=card, headers=waccessapi_header, params=(("callAction", False),))
    if card:
        print(f'Cartão criado com CardID = {card["CardID"]}.') 
        return(card)
    else:
        print(f'Erro ao criar cartão com ClearCode = {new_card["ClearCode"]}.')

def check_card(user_list, companie_list):
    card_name = str(user_list["CHID"])
    card_name = f'F_{card_name.zfill(9)}' 
    new_card = { "ClearCode": card_name, "CardNumber": user_list["CHID"], "FacilityCode": 0, "CardType": 0, "PartitionID": companie_list["PartitionID"], "IsAutomaticCard": True }
    get_card = requests.get(waccessapi_endpoint + f'cards', params=(("limit", 1),("ClearCode", card_name)))
    get_card_json = get_card.json()
    if not get_card_json:
        card = create_card(new_card, user_list)
    else:
        print(f'Cartão {card_name} já existe')
        for card_object in get_card_json:
            requests.post(waccessapi_endpoint + f'cardholders/{user_list["CHID"]}/cards', json=card_object, headers=waccessapi_header, params=(("callAction", False),))
            print('Cartão vinculado')

try:
    with open('teste.csv', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter= ',')
        #csv_reader.__next__()
        end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
        end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")
        for row in csv_reader:
            try:
                cpf = row[1].replace(".", "").replace("-", "")
                user = {"FirstName" : row[0],
                        "IdNumber" : cpf,
                        "AuxText09" : row[2],
                        "CHType" : int(row[3]),
                        "CompanyID": row[5],
                        "PartitionID" : 1,
                        "CHState" : 0,
                        "CHEndValidityDateTime" : end_validity_str}
                print(f'Importando {user["FirstName"]} - {user["IdNumber"]}') 
                user_post = requests.post(waccessapi_endpoint + 'cardholders', json=user, headers=waccessapi_header, params=(("callAction", False),))
                user_get = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("CHType", user["CHType"]),("IdNumber", user["IdNumber"])))
                user_get_json = user_get.json()
                if user_get_json:
                    for user_access in user_get_json:
                        companie = requests.get(waccessapi_endpoint + f'companies/' + str(user_access["CompanyID"]), headers=waccessapi_header)
                        companie_list = companie.json()
                        card = check_card(user_access, companie_list)
                        accesslevels = { "CHID" : user_access["CHID"], "AccessLevelID": int(row[4]) , "AccessLevelStartValidity": None , "AccessLevelEndValidity": None}
                        assing = requests.post(waccessapi_endpoint + f'cardholders/{user_access["CHID"]}/accessLevels/{int(row[4])}', json=accesslevels, headers=waccessapi_header, params=(("callAction", False),))
                        print('Importação OK') 
                else:
                    print(f'Erro ao Criar Usuário - {user["FirstName"]} - {user["IdNumber"]}')
                    with open('Not_Created.json', 'a', encoding='utf-8') as export:
                        json.dump(user, export, ensure_ascii=False, indent=4)
            except Exception as ex_user:
                report_exception(ex_user)
except Exception as ex:
        report_exception(ex)