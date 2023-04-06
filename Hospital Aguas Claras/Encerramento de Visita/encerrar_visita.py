# -*- coding: utf-8 -*-

import pyodbc, requests, json, sys, datetime
from GenericTrace import *
from encerrar_client import *

url = "http://localhost/W-AccessAPI/v1/"
h = { 'WAccessAuthentication': 'encerrar:#integra#', 'WAccessUtcOffset': '-180' }

# Visitor data
chtype = int(sys.argv[1]) # CHtype 8 = pacientes
chid = int(sys.argv[2])

# -------------------------------Testes --------------------------------
#chtype = 8 # CHtype 
#chid = 1 # CHID
# -------------------------------Testes --------------------------------


## ---------------------------- Begin -  --------------------------------------
trace(f'Updating visitor with contactCHID = {chid}')
if chtype != 8: # Colaboradores, Prestadores e Médicos
    trace(f'CHType not in (8), end process')
    sys.exit()

reply = requests.get(url + f'cardholders/searchGeneric', headers=h, params=(("CHType", '1'),("startedVisits", True),("includeTables", "ActiveVisit")))
reply_json = reply.json()

for user in reply_json:
    if user["ActiveVisit"]["ContactCHID"] == chid:
        getuser = requests.get(url + f'cardholders/{user["CHID"]}', headers=h)
        contactuser = getuser.json()
        end_validity_dte = datetime.utcnow() + timedelta(hours=1)
        end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")
        contactuser["CHEndValidityDateTime"] = end_validity_str
        reply = requests.put(url + 'cardholders', headers=h, json=contactuser, params=(("callAction", False),))
        if reply.reason == 'No Content':
            trace(f'Visitor: {contactuser["FirstName"]} updated, end visit: {contactuser["CHEndValidityDateTime"]}')

if not reply_json:
    trace('0 visitors with active visit.')
 
## ---------------------------- END -  --------------------------------------

