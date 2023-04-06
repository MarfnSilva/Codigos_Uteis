# -*- coding: utf-8 # -*- 

from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests, json, traceback, sys, base64, re
from unidecode import unidecode
from GenericTrace import report_exception, trace

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}


new_visit_obj = {
   "CHID": 2,
   "FirstName": '@VISITANTE',
   "ClearCode": 'VIS-321',
   "VisitEnd": "2022-02-25T12:47:12.578Z",
   "OperName": "invenzi",
   "VisAuxText01": "teste"
}

new_att = requests.post(waccessapi_endpoint + f'cardholders/{new_visit_obj["CHID"]}/activeVisit', headers=waccessapi_header, json=new_visit_obj, params=(("callAction", False),))

if new_att.status_code == requests.codes.created:
    print('Deu certo')
else:
    print('N deu Certo')