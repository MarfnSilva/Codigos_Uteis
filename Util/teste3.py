from GenericTrace import report_exception, trace
import requests, json, traceback, sys, base64, re, os, csv
from datetime import datetime, timedelta 
#from datetime import timedelta  
from requests.models import Response
import time
# user_chid = sys.argv[1]
# user_chtype = sys.argv[2]
# user_companyid = sys.argv[3]
#user_chid = 27356
#user_chtype = '2'
#user_companyid = '4'

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}


def create_card(new_card, user_list):
    print(f'Creating new card.')
    create_card = requests.post(waccessapi_endpoint + f'cards', json=new_card)
    card = create_card.json()
    requests.post(waccessapi_endpoint + f'cardholders/{user_list["CHID"]}/cards', json=card, headers=waccessapi_header, params=(("callAction", False),))
    if card:
        print(f'Cartão criado com CardID = {card["CardID"]}.') 
        #return(card)
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

user = requests.get(waccessapi_endpoint + f'cardholders', headers=waccessapi_header, params=(("CHType", (1 , 7)),("limit", '1000')))
user_list  = user.json()
print(user_list)
# for wxs_user in user_list:
#     companie = requests.get(waccessapi_endpoint + f'companies/' + str(wxs_user["CompanyID"]), headers=waccessapi_header)
#     companie_list = companie.json()
#     card = check_card(wxs_user, companie_list)
#     time.sleep(0.3)

# linked = { "CHID": 5, "LinkedCHID": 669, "EscortsLinkedCH": False, "EscortedByLinkedCH": False }
# reply = requests.post(waccessapi_endpoint + f'cardholders/{5}/linkedCardholders', headers=waccessapi_header, json=linked, params=(("callAction", False),))
# reply_json = reply.json()
# print(reply_json)