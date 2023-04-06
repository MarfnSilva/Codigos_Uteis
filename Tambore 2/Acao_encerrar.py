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

#*************************************************Ação ao Encerrar Visita************************************************ 
url = WxsConn.waccessapi_endpoint
h = WxsConn.waccessapi_header

chid = int(sys.argv[1]) 

#chid = '20560'

reply = requests.delete(url + f'cardholders/{chid}/activeVisit',headers=h, params=(("callAction", False),) )
#delete_visit=reply.json()

#print(delete_visit)


