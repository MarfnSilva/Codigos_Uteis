# coding: utf-8

import requests, json, traceback, sys, base64, sqlite3
from datetime import datetime  
from datetime import timedelta  
from GenericTrace import trace, report_exception
from WXSConnection import *

def updateUser(updated_wxs_user):
    
    # ---------------------------------- Update Cardholder  ----------------------------------- 
    print(updated_wxs_user["FirstName"])
    print("\n* Cardholders - Update")
    trace(updated_wxs_user["IdNumber"], 'Cardholders - Update', color='DarkOrange')
        
    #--------- update cardholder validity -----------
    now = datetime.now() + timedelta(days=3600)
    updated_wxs_user["CHEndValidityDateTime"] = now.strftime("%Y-%m-%dT%H:%M:%S")

    reply = requests_put('cardholders', json=updated_wxs_user)
    
    if reply.status_code == requests.codes.no_content:
        print(f"Cardholder {updated_wxs_user['FirstName']} - update OK")
        trace(updated_wxs_user["IdNumber"], f"Cardholder {updated_wxs_user['FirstName']} - update OK", color='DarkOrange')

        # ------------------- Assign Entry Access Level --------------
        EntryAccessLevel = '29'
        chAccessLevel = { "CHID": str(updated_wxs_user["CHID"]), "AccessLevelID": EntryAccessLevel , "AccessLevelStartValidity":str(datetime.now()), "AccessLevelEndValidity": updated_wxs_user["CHEndValidityDateTime"]}
        AddAccessLevel = requests_post('cardholders/' + str(updated_wxs_user["CHID"]) + '/accessLevels/' + EntryAccessLevel, json=chAccessLevel)
    else:
        trace(updated_wxs_user, "Error: " + reply.json()["Message"], color='IndianRed')

def createCard(cardholder):

    if cardholder["CHState"] != 0:
        return
    
    FuncCard = requests_get('cardholders/' + str(cardholder["CHID"]) + '/cards') # CardType = 0 >> Residente
    FuncCard_json = FuncCard.json()
    if FuncCard.status_code == requests.codes.ok:
        for card in FuncCard_json:
            if cardholder["CHState"] == 0:
                card["CardState"] = 0
                reply = requests_put('cards', json=card)
            else:
                card["CardState"] = 1
                reply = requests_put('cards', json=card)

def checkStatus(user, wxs_visits_dict, wxs_acomp_dict):
    if user["IdNumber"]:
        idnumber = user["IdNumber"].replace(".", "").replace("-","")
        wxs_visit = wxs_visits_dict.get(idnumber)
        wxs_acomp = wxs_acomp_dict.get(idnumber)
    else:
        wxs_visit = None
        wxs_acomp = None

    if user["CHState"] in range(1,8):
        print(f'user: {user["FirstName"]} Status (Inativo)')
        return(user["CHState"])

    if wxs_visit:
        print(f'user: {user["FirstName"]} Status (Com Atendimento ativo)')
        status = 9 # CHState = 9 >> Em Atendimento
        return(status)

    elif wxs_acomp:
        print(f'user: {user["FirstName"]} Status (Com Atendimento ativo)')
        status = 9 # CHState = 9 >> Em Atendimento
        return(status)

    elif user["CHState"] == 9:
        print(f'user: {user["FirstName"]} Status (Com Atendimento ativo)')
        status = 0 # CHState = 0 >> Ativo
        return(status)

    else:
        return(user["CHState"])


def db_connection():
    database = 'acomp_integra.db'
    if os.path.isfile(database):
        conn = sqlite3.connect(database)
        return(conn)
    else:
        print('Não existe')
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE RemovedAccessLevels (CHID INTEGER UNIQUE NOT NULL, RemovedAccessLevelIDs TEXT);""")
        print('Tabela criada com sucesso.')
        sql = ("CREATE INDEX index_chid ON RemovedAccessLevels (CHID);")
        cursor.execute(sql)
        return(conn)


def insert_local_db(chid):
    conn = db_connection()
    script = f""" INSERT INTO RemovedAccessLevels (CHID, RemovedAccessLevelIDs) values ({chid}, null) """
    cur = conn.cursor()
    cur.execute(script)
    conn.commit()
    conn.close()


def write_local_db(chid, removedAC):
    conn = db_connection()
    script = f""" UPDATE RemovedAccessLevels set RemovedAccessLevelIDs = '{removedAC}' where chid = {chid} """
    cur = conn.cursor()
    cur.execute(script)
    conn.commit()
    conn.close()


def read_local_db(chid):
    conn = db_connection()
    script = f""" SELECT * from RemovedAccessLevels where chid = {chid} """
    cur = conn.cursor()
    c = cur.execute(script)
    result = c.fetchall()
    if not result:
        insert_local_db(chid)
        return(None)
    else:
        for wxs_chid, accesslevels in result:
            print(wxs_chid, accesslevels)
            return(accesslevels)
    conn.commit()
    conn.close()
    return()