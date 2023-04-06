# -*- coding: utf-8 # -*- 

#from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests#, json, traceback, sys, base64, re
# from GenericTrace import report_exception, trace

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}


endpoint = 'http://ws.hubdodesenvolvedor.com.br/v2/cnpj/'
cnpj='34885930000191'#'00000000000191'
token = '115044595wckPIDtWBy207709528'

user = requests.get(endpoint, params=(("cnpj", cnpj),("token", token)))
get_user  = user.json()
if get_user["result"]:
    print(get_user["result"]["nome"])
    print(get_user["result"]["fantasia"])
    print(get_user["result"]["logradouro"])
    print(get_user["result"]["numero"])
    print(get_user["result"]["municipio"])
    print(get_user["result"]["cep"])
    print(get_user["result"]["uf"])
    
