# -*- coding: utf-8 # -*- 

from GenericTrace import report_exception, trace
import pyodbc,requests, json, traceback, sys, re, os, csv#,base64
from datetime import datetime  
from datetime import timedelta  
from requests.models import Response
import time
#from WXSConnection import *

waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

def generate_plate(plate):
    reply = requests.get(waccessapi_endpoint + 'cards/licensePlates/cardNumber', headers=waccessapi_header, params=(("licensePlateText", plate),))
    card_plate = reply.json()
    return(card_plate)

def assign_card_plate(wxs_user, card_plate, companie_list):
    new_card = { "ClearCode": wxs_user["FirstName"], "CardNumber": card_plate, "FacilityCode": 0, "CardType": 0, "PartitionID": companie_list["PartitionID"], "IsAutomaticCard": True }
    get_card = requests.get(waccessapi_endpoint + 'cards', headers=waccessapi_header, params=(("limit", 30000),("ClearCode", wxs_user["FirstName"])))
    get_card_json = get_card.json()
    if not get_card_json:
        card = create_card_car(new_card)
    elif get_card.status_code == requests.codes.ok:
        card = get_card.json()

    assign_card = requests.post(waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/cards', headers=waccessapi_header, json=card, params=(("callAction", False),))
    
def assign_access_level(wxs_user):
    reply = requests.post(waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/accessLevels/287', headers=waccessapi_header, json={}, params=(("callAction", False),))

def associate_to_cardholder(chid, card_chid):
    linked = { "CHID": chid, "LinkedCHID": card_chid, "EscortsLinkedCH": False, "EscortedByLinkedCH": False }
    reply = requests.post(waccessapi_endpoint + f'cardholders/{chid}/linkedCardholders', headers=waccessapi_header, json=linked, params=(("callAction", False),))
        
def create_card_car(new_card):
    print(f'Creating new card.')
    create_card = requests.post(waccessapi_endpoint + 'cards', headers=waccessapi_header, json=new_card, params=(("callAction", False),))
    card = create_card.json()
    if card:
        print(f'Card created with cardID = {card["CardID"]}')
        return(card)
    else:
        print(f'Error creating card with clearcode = {new_card["ClearCode"]}')

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
    with open('teste_02.csv', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter= ',')
        #csv_reader.__next__()
        end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
        end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")
        for row in csv_reader:
            try:
                placa = [] #row[3].replace('-', '')
                cpf = row[1].replace(".", "").replace("-", "")
                user = {"FirstName" : row[0], "IdNumber" : cpf, "CHType" : int(row[8]), "CompanyID": row[7], "PartitionID" : row[9], "CHState" : 0, "CHEndValidityDateTime" : end_validity_str}

                print(f'Importando {user["FirstName"]} - {user["IdNumber"]}') 
                user_post = requests.post(waccessapi_endpoint + 'cardholders', json=user, headers=waccessapi_header, params=(("callAction", False),))
                user_get = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("CHType", user["CHType"]),("IdNumber", user["IdNumber"])))
                user_get_json = user_get.json()
                if user_get_json:
                    for user_access in user_get_json:
                        companie = requests.get(waccessapi_endpoint + f'companies/' + str(user_access["CompanyID"]), headers=waccessapi_header)
                        companie_list = companie.json()
                        partition_car = int(companie_list["PartitionID"])
                        card = check_card(user_access, companie_list)
                        accesslevels = { "CHID" : user_access["CHID"], "AccessLevelID": int(row[2]) , "AccessLevelStartValidity": None , "AccessLevelEndValidity": None}
                        assing = requests.post(waccessapi_endpoint + f'cardholders/{user_access["CHID"]}/accessLevels/{int(row[2])}', json=accesslevels, headers=waccessapi_header, params=(("callAction", False),))
                        if placa:
                            placa = placa.replace('-', '')
                            get_vehicle = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("nameSearch", placa),("CHType", 4),("includeTable", "Cards")))
                            get_vehicle = get_vehicle.json()

                            if get_vehicle:
                                print('Carro encontrado')
                                for wxs_user in get_vehicle:
                                    print(f'Placa: {wxs_user["FirstName"]}')
                                    card_plate = generate_plate(placa)
                                    assign_card_plate(wxs_user, card_plate)
                                    assign_access_level(wxs_user)
                                    associate_to_cardholder(user_access["CHID"], wxs_user["CHID"])
                                
                            else:
                                print('Carro não encontrado')
                                new_car = { "FirstName": placa, "CHType": 4, "PartitionID": row[9], "AuxText01": row[4], "AuxText02" : row[5], "AuxText03" : row[6]}
                                reply = requests.post(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, json=new_car, params=(("callAction", False),))
                                reply_json = reply.json()
                                print(reply_json)
                                if reply.status_code == requests.codes.created:
                                        print(f"New CHID: {reply_json['CHID']}")
                                        wxs_user = reply_json
                                        card_plate = generate_plate(placa)
                                        assign_card_plate(wxs_user, card_plate, companie_list)
                                        assign_access_level(wxs_user)
                                        associate_to_cardholder(user_access["CHID"], wxs_user["CHID"])

                                else:
                                    print("Error: " + reply_json["Message"])

                    print('Importação Realizada')                     
                else:
                    print(f'Erro ao Criar Usuário - {user["FirstName"]} - {user["IdNumber"]}')
                    with open('Not_Created.json', 'a', encoding='utf-8') as export:
                        json.dump(user, export, ensure_ascii=False, indent=4)
            except Exception as ex_user:
                report_exception(ex_user)
except Exception as ex:
        report_exception(ex)