# -*- coding: utf-8 # -*- 

from matplotlib.font_manager import json_dump
from GenericTrace import report_exception, trace
import requests, json
from datetime import datetime, timedelta   
from Functions import *

#AuxText03 Nome Motorista


user_chid = '8132'
user_chtype = 5

user = requests.get(waccessapi_endpoint + f'cardholders/' + str(user_chid), headers=waccessapi_header, params=(("CHType", user_chtype),("limit", '20000')))
get_user  = user.json()

global settings
settings = json.loads(open('visit.json').read())

end_validity_dte = datetime.now() #+ timedelta(days=1825) # 1825 Days = 5 Years
end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")


settings['visit']['id'] = end_validity_str # Horário da impressão
settings['visit']['checkinType'] = get_user['FirstName'] # Nome da Folha de Fluxo
settings['visit']['checkinByIpadId'] = get_user['AuxText02'].upper()# Nome Transportadora
settings['visit']['countryCode'] = get_user['AuxText01'].upper()# CNPJ Transportadora
settings['visit']['phone'] = get_user['AuxText03'].upper()# Nome Motorista
settings['visit']['createdAt'] = get_user['IdNumber']# CPF Motorista
settings['visit']['updatedAt'] = get_user['AuxText04']# CNH Motorista
settings['visit']['deletedAt'] = get_user['AuxText09'].upper()# Placa Cavalo/Truck
settings['visit']['expectedAt'] = get_user['AuxText10'].upper()# Placa Carreta 1
settings['visit']['checkoutType'] = get_user['AuxText11'].upper()# Placa Carreta 2
settings['visit']['finishCheckinAt'] = get_user['AuxTextA01'].upper()# Lacre Entrada
settings['visit']['checkoutAt'] = get_user['AuxTextA02'].upper()# Lacre Saída
settings['visit']['authorizedById'] = get_user['AuxText12'].upper()# Nota Fiscal


# settings['visit']['name'] = get_user['AuxText03']


# print(settings['visit']['name'])

print_post = requests.post('http://172.16.17.191:7677/api/reports', json=settings)
print(f'{print_post.status_code} - {print_post.reason}')







