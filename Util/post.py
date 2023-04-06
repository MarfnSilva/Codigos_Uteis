# -*- coding: utf-8 # -*- 

from GenericTrace import report_exception, trace
import requests, json, traceback, sys, base64, re, os, csv
from datetime import datetime  
from datetime import timedelta  
from requests.models import Response
import time
from WXSConnection import *

waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'ValidadeASO:#TesteAPI01#', 'WAccessUtcOffset': '-180'}

end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")

user = {"FirstName" : "teste_post",
        "IdNumber" : "123456",
        "AuxText09" : "123",
        "CHType" : 3,
        "PartitionID" : 1,
        "CHState" : 0,
        "CHEndValidityDateTime" : end_validity_str}

user_post = requests.post(waccessapi_endpoint + 'cardholders', json=user, headers=waccessapi_header, params=(("callAction", False),))
print(f'Importando {user["FirstName"]} - {user["IdNumber"]}') 