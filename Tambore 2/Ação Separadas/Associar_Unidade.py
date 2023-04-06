# -*- coding: utf-8 # -*- 
from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests, json, traceback, sys, base64, re
from GenericTrace import report_exception, trace
from WXSConnection import *
import pyodbc, requests, json, traceback, sys, csv
import os


trace("\n* Tambore 2 : v1.00 - 09/06/2021 12:06 ")

url = WxsConn.waccessapi_endpoint
h = WxsConn.waccessapi_header

#chid = sys.argv[1]
#comboIndex = int(sys.argv[2])

chid = '52'
fieldID = 'lstBDA_AuxLst02'
comboIndex = 0

trace("\n* Get all Lista Unidade - by index")
reply = requests.get(url + 'chComboFields', headers=h, params = (("chtype",2),("fieldID", fieldID), ("comboIndex", comboIndex)))
wxs_unidade_list = reply.json()

trace("\n* Get all Unidade - by index")
reply = requests.get(url + 'cardholders', headers=h, params = (("chtype",7),))
wxs_unidades = reply.json()

trace("\n* Get  Moradores - by IdNumber")
# ---------------------------------- Get all users in W-Access DB -----------------------------------
reply = requests.get(url + f'cardholders/{chid}', headers=h)
wxs_users = reply.json()

for u in wxs_unidade_list:
    if wxs_users["AuxLst02"] == u["ComboIndex"]:
        unidade=u["strLanguage2"]
        
print(unidade)

for un in wxs_unidades:
    if f"{unidade}" == un["FirstName"]:
        chid_unidade=un["CHID"] 

print(chid_unidade)

linked_chid = {
            "CHID": chid_unidade,
            "LinkedCHID": chid,
            "EscortsLinkedCH": False,
            "EscortedByLinkedCH": False
            }

reply = requests.post(url + f'cardholders/{chid_unidade}/linkedCardholders', json=linked_chid,headers=h) 
link = reply.json()
print(link)
sys.exit()