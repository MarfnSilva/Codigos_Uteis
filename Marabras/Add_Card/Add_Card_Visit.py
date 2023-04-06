# -*- coding: utf-8 -*-
#from GenericTrace import report_exception, trace
import requests, sys

user_chid = str(sys.argv[1])
user_chtype = int(sys.argv[2])
user_partitionid = int(sys.argv[3])
user_name = str(sys.argv[4])

# user_chid = '11491'
# user_chtype = 1
# # user_companyid = '23'
# user_partitionid = 41

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
url = 'http://localhost/W-AccessAPI/v1/'
h = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

servername = 'W-ACCESS-SRV-HO\W_ACCESS'
userid = 'sa'
password = '#w_access_Adm#'
databasename = 'W_Access'
odbcdriver = '{ODBC driver 17 for SQL Server}'

def generate_plate(plate):
    reply = requests.get(url + 'cards/licensePlates/cardNumber', headers=h, params=(("licensePlateText", plate),))
    card_plate = reply.json()
    return(card_plate)

def assign_card_plate(wxs_user, card_plate, partition_companyid):
    new_card = { "ClearCode": wxs_user["FirstName"], "CardNumber": card_plate, "FacilityCode": 0, "CardType": 0, "PartitionID": int(partition_companyid), "IsAutomaticCard": True }
    get_card = requests.get(url + 'cards', headers=h, params=(("limit", 30000),("ClearCode", wxs_user["FirstName"])))
    get_card_json = get_card.json()
    if not get_card_json:
        card = create_card_car(new_card)
    else:
        card = get_card.json()
    assign_card = requests.post(url + f'cardholders/{wxs_user["CHID"]}/cards', headers=h, json=card, params=(("callAction", False),))

def create_card_car(new_card):
    # trace(f'Creating new card.')
    create_card = requests.post(url + 'cards', headers=h, json=new_card, params=(("callAction", False),))
    card = create_card.json()
    # if card:
    #     # trace(f'Card created with cardID = {card["CardID"]}')
    #     return(card)
    # else:
    #     trace(f'Error creating card with clearcode = {new_card["ClearCode"]}')




def create_card(new_card, user_chid):
    create_card = requests.post(url + f'cards', json=new_card)
    card = create_card.json()
    requests.post(url + f'cardholders/{user_chid}/cards', json=card, headers=h, params=(("callAction", False),))

def check_card(user_chid, partition_card, name, card_type):
    card_name = str(user_chid)
    card_name = f'{name}_{card_name.zfill(9)}' 
    new_card = { "ClearCode": card_name, "CardNumber": user_chid, "FacilityCode": 0, "CardType": card_type, "PartitionID": partition_card, "IsAutomaticCard": True }
    get_card = requests.get(url + f'cards', params=(("limit", 1),("ClearCode", card_name)))
    get_card_json = get_card.json()
    if not get_card_json:
        card = create_card(new_card, user_chid)
    else:
        for card_object in get_card_json:
            requests.post(url + f'cardholders/{user_chid}/cards', json=card_object, headers=h, params=(("callAction", False),))

if user_chtype in (1, 7):
    partition_card = 0
    name = "VIS"
    card_type = 1
    check_card(user_chid, partition_card, name, card_type)
    assign = requests.post(url + f'cardholders/{str(user_chid)}/accessLevels/11', headers=h, json={}, params=(("callAction", False),))

    if user_partitionid != 1:
       get_user = requests.get(url + f'cardholders/{str(user_chid)}', headers=h)
       wxs_user = get_user.json()
       wxs_user["PartitionID"] = 1
       put_user = requests.put(url + f'cardholders', headers=h, json=wxs_user, params=(('callAction', False),))

elif user_chtype == 4:
    card_plate = generate_plate(user_name)
    assign_card_plate(user_chid, card_plate, partition_companyid)

else:
    sys.exit()