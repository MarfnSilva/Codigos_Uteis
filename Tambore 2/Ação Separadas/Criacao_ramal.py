from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests, json, traceback, sys, base64, re
from GenericTrace import report_exception, trace
from WXSConnection import *
import pyodbc, requests, json, traceback, sys, csv
import os


# ----------------------------------- Reading CCure Users -------------------------------------
servername = WxsConn.ccure_sql_servername
userid = WxsConn.ccure_sql_userid
password = WxsConn.ccure_sql_password
databasename = WxsConn.ccure_sql_databasename

conn = pyodbc.connect('Driver={ODBC driver 17 for SQL Server};Server='+servername+  ';UID='+userid+';PWD='+password+';Database='+databasename) 
cursor = conn.cursor()


set_chid = pyodbc.connect('Driver={ODBC driver 17 for SQL Server};Server='+servername+  ';UID='+userid+';PWD='+password+';Database='+databasename) 
set_chid = set_chid.cursor()

cursor.execute('select max (auxtext08) from chaux, chmain where chaux.chid=chmain.chid and chtype=2')
for row in cursor:
    ultimo_ramal =  int(row[0])

ramal_new = ultimo_ramal + 1

print(ultimo_ramal)
print(ramal_new)