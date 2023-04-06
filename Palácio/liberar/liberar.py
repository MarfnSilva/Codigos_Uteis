# -*- coding: utf-8 # -*- 

from hamcrest import contains
from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests,sys, pyodbc
from unidecode import unidecode
from GenericTrace import report_exception, trace
import configparser

parser = configparser.ConfigParser()
parser.read("Import.cfg")
servername = parser.get("config", "servername")
userid = parser.get("config", "userid")
password = parser.get("config", "password")
databasename = parser.get("config", "databasename")
odbcdriver = parser.get("config", "odbcdriver")
diretorio = parser.get("config", "diretorio")
api_server_name = parser.get("config", "api_server_name")
api_user = parser.get("config", "api_user")
api_password = parser.get("config", "api_password")


url = f'http://{api_server_name}/W-AccessAPI/v1/'
h = { 'WAccessAuthentication': f'{api_user}:{api_password}', 'WAccessUtcOffset': '-180'}

#Servidor Palacio - 'NORION-31741\W_ACCESS' 

user_chid = sys.argv[1]
# user_auxlist = int(sys.argv[2])
# user_chtype = int(sys.argv[3])

# user_chid = 5546

assign = requests.post(url + f'cardholders/{str(user_chid)}/accessLevels/66', headers=h, json={}, params=(("callAction", False),))
