# -*- coding: utf-8 -*-

from GenericTrace import report_exception, trace
import requests, csv   
from requests.models import Response
#from WXSConnection import *

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

i = 0
with open('Pacientes_Ativos_21-12-2021_v2.csv', encoding="utf8") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter= ';')
    for row in csv_reader:
        try:
            wxs_chid = row[0]
            wxs_del = row[5]
            if wxs_del == 'S':
                delvisit = requests.delete(waccessapi_endpoint + f'cardholders/{wxs_chid}/activeVisit', headers=waccessapi_header, params=(("callAction", False),))
                print(f'CHID {wxs_chid} - Visita Encerrada')
                i += 1
        except Exception as ex_user:
            report_exception(ex_user)
print(f'{i} Visitas Encerradas')       
        