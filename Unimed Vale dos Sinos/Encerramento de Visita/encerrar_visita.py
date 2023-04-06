# -*- coding: utf-8 -*-

import pyodbc, requests, json, sys, datetime
from GenericTrace import *
from encerrar_client import *

url = "http://w-access.unimedvs.com.br/W-AccessAPI/v1/"
h = { 'WAccessAuthentication': 'encerrar:#integra#', 'WAccessUtcOffset': '-180' }

try:
    # Visitor data
    chtype = int(sys.argv[1]) # CHtype 7 = pacientes
    chid = int(sys.argv[2])
    trace(f'Parameters recieved: CHType= {chtype} and CHID= {chid} ')
    # -------------------------------Testes --------------------------------
    #chtype = 7 # CHtype 
    #chid = 62887 # CHID 62887
    #trace(f'Parameters recieved [Teste]: CHType= {chtype} and CHID= {chid} ')
    # -------------------------------Testes --------------------------------


    ## ---------------------------- Begin -  --------------------------------------
    trace(f'Updating visitor with contactCHID = {chid}')
    if chtype != 7: # Colaboradores, Prestadores e Médicos
        trace(f'CHType not in (7), end process')
        sys.exit()

    reply = requests.get(url + f'cardholders/searchGeneric', headers=h, params=(("CHType", '1'),("startedVisits", True),("includeTables", "ActiveVisit")))
    reply_json = reply.json()
    trace(f'Get visitors: {reply.reason}')

    for user in reply_json:
        if user["ActiveVisit"]["ContactCHID"] == chid:
            getuser = requests.get(url + f'cardholders/{user["CHID"]}', headers=h)
            contactuser = getuser.json()
            trace(f'Updating visitor: {contactuser["FirstName"]}')
            end_validity_dte = datetime.utcnow() + timedelta(hours=4)
            end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")
            contactuser["CHEndValidityDateTime"] = end_validity_str
            reply = requests.put(url + 'cardholders', headers=h, json=contactuser, params=(("callAction", False),))
            if reply.reason == 'No Content':
                trace(f'Visitor: {contactuser["FirstName"]} updated, end visit: {contactuser["CHEndValidityDateTime"]}')

    if not reply_json:
        trace('0 visitors with active visit.')
    
    ## ---------------------------- END -  --------------------------------------

except Exception as ex:
    report_exception(ex)