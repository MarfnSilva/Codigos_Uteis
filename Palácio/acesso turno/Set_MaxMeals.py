# -*- coding: utf-8 # -*-  
from datetime import *
import pyodbc
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

conn = pyodbc.connect('Driver='+odbcdriver+';Server='+servername+';UID='+userid+';PWD='+password+';Database='+databasename) 
cursor = conn.cursor()
conn.autocommit = True

script = f"USE W_Access \
UPDATE CHMain \
SET MaxMeals = 1, CHDownloadRequired = 1 \
FROM CHMain \
INNER JOIN CHCards ON CHMain.CHID = CHCards.CHID \
WHERE CardState = 0 AND CHType = 2 AND CHState = 0 AND CHMain.CHID IN (SELECT CHID FROM CHGroups)" #lvl_id.append(sql_row[0])
cursor.execute(script)