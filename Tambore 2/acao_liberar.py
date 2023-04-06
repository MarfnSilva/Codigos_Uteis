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

#*************************************************Criar Cartão Com Base Na Placa************************************************ 

trace("\n* Tambore 2 : v1.00 - 22/06/2021 12:00 ")

url = WxsConn.waccessapi_endpoint
h = WxsConn.waccessapi_header

chid = sys.argv[1]
chtype= sys.argv[2]
#chid = 21759
#chtype=5

#-------------------------------------------------- Get User --------------------------------------------------------------------------------------

reply = requests.get(url + f'cardholders/{chid}', headers=h, params=(("chtype",{chtype}),))
wxs_users = reply.json()

if not wxs_users["AuxText03"]:
    print('Add Card')

else:
    
    placa= wxs_users["AuxText03"]

    print(placa)

    #---------------------------------------------------Get Cartão --------------------------------------------------------------------------------------- 
    reply = requests.get(url +f'cards',headers=h, params=(("ClearCode",placa),))
    get_cartao=reply.json()

    print(reply.status_code)
    print(get_cartao)


    for c in get_cartao:
            print(c)
            if placa == c["ClearCode"]:
                placa_2=c["ClearCode"]

            print(placa_2)         
                
    if get_cartao:
        print('entrei')
        placa_2=placa
        print(placa_2)
    else:
        placa_2=''


    #---------------------------------------------------------------------------------------------------------------------------------------------------- 


    if placa !=placa_2:  

        reply= requests.get(url+ f'cards/licensePlates/cardNumber?licensePlateText={placa}')
        card_placa = reply.json()
        print(card_placa)
        linked_card = {
                "ClearCode":placa,
                "CardNumber":card_placa,
                "FacilityCode": 0,
                "CardType": 0,
                "PartitionID": 0,
                "CardEndValidityDateTime": wxs_users["CHEndValidityDateTime"]
                        }             
    
        #print(linked_card)

        create_card = requests.post(url + 'cards', headers=h, json=linked_card , params = (("callAction", False),))
        create_card_json = create_card.json()
        create_card_json["CHID"] = wxs_users["CHID"]

        #print(create_card_json)

        reply= requests.post(url+ f'cardholders/{chid}/cards', headers=h, json= create_card_json , params = (("callAction", False),))
        associacao=reply.json()

        #print(create_card_json)

    else:
        print('entrei aqui')
        print(type(get_cartao))

        for c in get_cartao:
            print(c)
            if placa == c["ClearCode"]:
                cardid=c["CardID"]

            print(cardid)
            
            reply= requests.delete(url+ f'cardholders/{chid}/cards/{cardid}')

            c["CHID"] = wxs_users["CHID"]
            
            reply= requests.post(url+ f'cardholders/{chid}/cards', headers=h, json= c , params = (("callAction", False),))
            associacao=reply.json()

            print(associacao)