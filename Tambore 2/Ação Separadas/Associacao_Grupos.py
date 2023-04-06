# Morador 2
# Inquilino 3
# Visitente 4 

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
#comboIndex_tipo = int(sys.argv[2])

chid = '52'
fieldID = 'lstBDA_AuxLst02'
comboIndex_tipo = 2
check_auto=0

if comboIndex_tipo == 0:
    group_id=2
elif comboIndex_tipo == 1:
    group_id=3
elif comboIndex_tipo==2 and check_auto ==0:
    group_id=4
elif comboIndex_tipo==2 and check_auto ==1:
    group_id=6
else:
    group_id=None


trace("\n* Get  Moradores - by IdNumber")
# ---------------------------------- Get all users in W-Access DB -----------------------------------
reply = requests.get(url + f'cardholders/{chid}', headers=h)
wxs_users = reply.json()

trace("\n* Grupo Associado - by IdNumber")
reply = requests.post(url + f'cardholders/{chid}/groups/{group_id}', headers=h) 
sys.exit()