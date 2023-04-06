





from typing import no_type_check
from GenericTrace import trace
import requests, json, traceback, sys, base64, re, os
from datetime import datetime  
#import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta  
from requests.models import Response
import time
from WXSConnection import *

#new_att = requests.get('http://localhost/W-AccessAPI/v1/cardholders/searchGeneric', headers=WxsConn.waccessapi_header, params=(("CHType", 8),("startedVisits", True)))
#reply_json = new_att.json()


#for user in reply_json:
 #   del_vis = requests.delete(f'http://localhost/W-AccessAPI/v1/cardholders/{user["CHID"]}/activeVisit', headers=WxsConn.waccessapi_header)



waccess_api_server = 'localhost'
waccess_api_user = 'WAccessAPI'
waccess_api_password = '#WAccessAPI#'
waccess_utc_offset = '-180'

waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'testeAPI:#testeAPI#', 'WAccessUtcOffset': '-180'}

wxs_user = {
    "CHID": 6
}


def create_card(chid):
    print('Criando o cartão')

    nex_card = {
    "ClearCode": f'BIO_{str(wxs_user["CHID"]).zfill(9)}',
    "CardNumber": wxs_user["CHID"],
    "FacilityCode": 0,
    "CardType": 1,
    "CardState": 8,
    "PartitionID": 0,
    }

    createcard = requests.post(waccessapi_endpoint + f'cards', headers=waccessapi_header, json=nex_card)
    print(f'Create card response: {createcard.reason}')

    return(createcard.json())

def get_attendence(chid):
    get_active_visit = requests.get(waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/activeVisit', headers=waccessapi_header)
    get_active_visit_json = get_active_visit.json()
    get_active_visit_json["CHID"] = chid
    return(get_active_visit_json)

def start_visit(chid, obj_visit, card):
    obj_visit["CHID"] = chid
    obj_visit["ClearCode"] = card
    new_visit = requests.post(waccessapi_endpoint + f'cardholders/{chid}/activeVisit', headers=waccessapi_header, json=obj_visit, params=(("callAction", False),))
    print(f'Liberação da nova visita | {new_visit.reason}')    

get_card = requests.get(waccessapi_endpoint + 'cards', headers=waccessapi_header, params=(("limit", 1),("cardType", 1), ("ClearCode", f'BIO_{str(wxs_user["CHID"]).zfill(9)}' )))
get_card_json = get_card.json()

if get_card_json:
    for cartao in get_card_json :
        print('Achou o cartao')
        obj_visit = get_attendence(wxs_user["CHID"])
        delvisit = requests.delete(waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/activeVisit', headers=waccessapi_header, params=(("callAction", False),))
        print(f'Encerra visita atual | {delvisit.reason}')
        #start_visit(wxs_user["CHID"], obj_visit, cartao["ClearCode"])
        continue
        
else:
    print('sem cartão')
    card = create_card(wxs_user["CHID"])
    obj_visit = get_attendence(wxs_user["CHID"])
    delvisit = requests.delete(waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/activeVisit', headers=waccessapi_header, params=(("callAction", False),))
    print(f'Encerra visita atual | {delvisit.reason}')
    #start_visit(wxs_user["CHID"], obj_visit, card["ClearCode"])
