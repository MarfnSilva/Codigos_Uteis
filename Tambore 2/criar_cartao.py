# -*- coding: utf-8 # -*- 

from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests, json, traceback, sys, base64, re
from GenericTrace import report_exception, trace
from WXSConnection import *
import pyodbc, requests, json, traceback, sys, csv
import os
from dateutil.relativedelta import relativedelta

#*************************************************Concatenação Rua************************************************ 

trace("\n* Tambore 2 : v1.00 - 09/06/2021 12:06 ")

url = WxsConn.waccessapi_endpoint
h = WxsConn.waccessapi_header

chid = 438

get_user = requests.get(url + f'cardholders/{chid}', headers=h, params=(("includetables","Cards"),))
get_user_json = get_user.json()

#print(get_user_json)

print(get_user_json["Cards"])

if get_user_json['Cards']:
    for card in get_user_json['Cards']:
        n_terminalip= card['IPRdrUserID']
        print(n_terminalip)
    
    if n_terminalip==None:
        print('cartão sem numero de terminal ip')
        linked_card = {
            "ClearCode":f'card_9000{chid}',
            "CardNumber":f'9000{chid}',
            "FacilityCode": 0,
            "CardType": 0,
            "PartitionID": 0,
            "IPRdrUserID":f'9000{chid}',
            "CardEndValidityDateTime": get_user_json["CHEndValidityDateTime"]
}             
        print(linked_card)
        create_card = requests.post(url + 'cards', headers=h, json=linked_card , params = (("callAction", False),))
        create_card_json = create_card.json()
        create_card_json["CHID"] = get_user_json["CHID"]
        
        reply = requests.get(url +f'cards',headers=h, params=(("ClearCode",f'carta_9000{chid}'),))
        get_cartao=reply.json()

        assign_card = requests.post(url + f'cardholders/{chid}/cards',headers=h, json=get_cartao, params=(("callAction", False),))
        assign_card = assign_card.json()

    print('usuario possui cartão')
else:
    print('usuario nao tem cartão')
