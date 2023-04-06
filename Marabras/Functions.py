# -*- coding: utf-8 # -*- 

from GenericTrace import report_exception, trace
import requests
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

waccessapi_endpoint = f'http://{api_server_name}/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': f'{api_user}:{api_password}', 'WAccessUtcOffset': '-180'}


def generate_plate(plate):
    reply = requests.get(waccessapi_endpoint + 'cards/licensePlates/cardNumber', headers=waccessapi_header, params=(("licensePlateText", plate),))
    card_plate = reply.json()
    return(card_plate)

def assign_card_plate(wxs_user, card_plate, partition_companyid):
    new_card = { "ClearCode": wxs_user["FirstName"], "CardNumber": card_plate, "FacilityCode": 0, "CardType": 0, "PartitionID": int(partition_companyid), "IsAutomaticCard": True }
    get_card = requests.get(waccessapi_endpoint + 'cards', headers=waccessapi_header, params=(("limit", 30000),("ClearCode", wxs_user["FirstName"])))
    get_card_json = get_card.json()
    if not get_card_json:
        card = create_card_car(new_card)
    else:
        card = get_card.json()
    assign_card = requests.post(waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/cards', headers=waccessapi_header, json=card, params=(("callAction", False),))
    
def assign_access_level(wxs_user, accesslvlid):
    reply = requests.post(waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/accessLevels/{accesslvlid}', headers=waccessapi_header, json={}, params=(("callAction", False),))

def associate_to_cardholder(chid, card_chid):
    linked = { "CHID": chid, "LinkedCHID": card_chid, "EscortsLinkedCH": False, "EscortedByLinkedCH": False }
    reply = requests.post(waccessapi_endpoint + f'cardholders/{chid}/linkedCardholders', headers=waccessapi_header, json=linked, params=(("callAction", False),))
        
def create_card_car(new_card):
    trace(f'Creating new card.')
    create_card = requests.post(waccessapi_endpoint + 'cards', headers=waccessapi_header, json=new_card, params=(("callAction", False),))
    card = create_card.json()
    if card:
        trace(f'Card created with cardID = {card["CardID"]}')
        return(card)
    else:
        trace(f'Error creating card with clearcode = {new_card["ClearCode"]}')

def create_card(new_card, user_list):
    trace(f'Creating new card.')
    create_card = requests.post(waccessapi_endpoint + f'cards', json=new_card)
    card = create_card.json()
    requests.post(waccessapi_endpoint + f'cardholders/{user_list["CHID"]}/cards', json=card, headers=waccessapi_header, params=(("callAction", False),))
    if card:
        trace(f'Cartão criado com CardID = {card["CardID"]}.') 
        return(card)
    else:
        trace(f'Erro ao criar cartão com ClearCode = {new_card["ClearCode"]}.')

def check_card(user_list, partitionid):
    card_name = str(user_list["CHID"])
    card_name = f'F_{card_name.zfill(9)}' 
    new_card = { "ClearCode": card_name, "CardNumber": user_list["CHID"], "FacilityCode": 0, "CardType": 0, "PartitionID": int(partitionid), "IsAutomaticCard": True }
    get_card = requests.get(waccessapi_endpoint + f'cards', params=(("limit", 1),("ClearCode", card_name)))
    get_card_json = get_card.json()
    if not get_card_json:
        card = create_card(new_card, user_list)
    else:
        trace(f'Cartão {card_name} já existe')
        for card_object in get_card_json:
            add_card = requests.post(waccessapi_endpoint + f'cardholders/{user_list["CHID"]}/cards', json=card_object, headers=waccessapi_header, params=(("callAction", False),))
            add_card_json = add_card.json()
            trace(add_card_json)
            trace('Cartão vinculado')