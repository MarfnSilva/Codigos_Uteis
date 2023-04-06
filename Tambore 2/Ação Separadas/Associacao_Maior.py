# -*- coding: utf-8 # -*- 
from requests.models import Response
import datetime
from datetime import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests, json, traceback, sys, base64, re
from GenericTrace import report_exception, trace
from WXSConnection import *
import pyodbc, requests, json, traceback, sys, csv
import os

trace("\n* Tambore 2 : v1.00 - 09/06/2021 12:06 ")

url = WxsConn.waccessapi_endpoint
h = WxsConn.waccessapi_header

chid = '52'

trace("\n* Get  Moradores - by IdNumber")
# ---------------------------------- Get all users in W-Access DB -----------------------------------
reply = requests.get(url + f'cardholders/{chid}', headers=h)
wxs_users = reply.json()

data_string=wxs_users["AuxDte02"]
data_now=datetime.now()
data_string=data_string.replace('T', ' ')

time_dte = datetime.strptime(data_string, '%Y-%m-%d %H:%M:%S').date()
now = datetime.now()

relative_date = relativedelta(now, time_dte)
idade = relative_date.years

if idade > 18:
    group_id=5
    print('Maior de idade')
    trace("\n* Grupo Associado - by IdNumber")
    reply = requests.post(url + f'cardholders/{chid}/groups/{group_id}', headers=h) 

else:
    print('Menor')

sys.exit()