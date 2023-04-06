# coding: utf-8

import requests, json, traceback, sys, base64, pyodbc
from datetime import datetime  
from datetime import timedelta  
from GenericTrace import trace

def updateUser(url, h, updated_wxs_user):
    
    # ---------------------------------- Update Cardholder  ----------------------------------- 

    trace("\n* Cardholders - Update")
    #writeTrace(unimed_user["IdNumber"], 'Cardholders - Update', color='DarkOrange')

    #--------- update cardholder validity -----------
    now = datetime.now() + timedelta(days=3600)
    updated_wxs_user["CHEndValidityDateTime"] = now.strftime("%Y-%m-%dT%H:%M:%S")
        
    reply = requests.put(url + 'cardholders', json=updated_wxs_user, headers=h, params = (("callAction", False),))
    
    if reply.status_code == requests.codes.no_content:
        trace(f"Cardholder {updated_wxs_user['FirstName']} - update OK")
        #writeTrace(unimed_user["IdNumber"], f"Cardholder {updated_wxs_user['FirstName']} - update OK", color='DarkOrange')

        # ------------------- Assign Entry Access Level --------------

        EntryAccessLevel = '98'
        chAccessLevel = { "CHID": str(updated_wxs_user["CHID"]), "AccessLevelID": EntryAccessLevel , "AccessLevelStartValidity":str(datetime.now()), "AccessLevelEndValidity": updated_wxs_user["CHEndValidityDateTime"]}
        AddAccessLevel = requests.post(url + 'cardholders/' + str(updated_wxs_user["CHID"]) + '/accessLevels/' + EntryAccessLevel, json=chAccessLevel, headers=h, params = (("callAction", False),))
        
        
    else:
        trace("Error: " + reply.json()["Message"])
        #writeTrace(unimed_user, "Error: " + reply.json()["Message"], color='IndianRed')


def createUser(url, h, unimed_user):

    # ---------------------------------- Create New Cardholder  ----------------------------------- 
    
    new_cardholder = None

    trace("\n* Cardholders - Create")
    new_cardholder = { "FirstName": unimed_user["FirstName"], "CHType": 3, "IdNumber": unimed_user["IdNumber"], "PartitionID": 1, \
        "AuxText08": unimed_user["AuxText08"], "AuxText10": unimed_user["AuxText10"], "AuxLst01": unimed_user["AuxLst01"], \
        "AuxText01": unimed_user["AuxText01"]}

    #new_cardholder["CHState"] = checkStatus(unimed_user) ## Check Unimed status to define CHState

    reply = requests.post(url + 'cardholders', json=new_cardholder, headers=h, params = (("callAction", False),))
    reply_json = reply.json()

    if reply.status_code == requests.codes.created:
        trace(f'New CHID: {reply_json["CHID"]} with FirstName: {reply_json["FirstName"]}')
        #writeTrace(unimed_user["IdNumber"],f'New CHID: {reply_json["CHID"]} with FirstName: {reply_json["FirstName"]}', color='DarkGreen')

        cardholder = reply_json
        #checkCard(url, h, cardholder)

        # ------------------- Assign Entry Access Level --------------

        EntryAccessLevel = '98'
        chAccessLevel = { "CHID": str(cardholder["CHID"]), "AccessLevelID": EntryAccessLevel , "AccessLevelStartValidity":str(datetime.now()), "AccessLevelEndValidity": cardholder["CHEndValidityDateTime"]}
        AddAccessLevel = requests.post(url + 'cardholders/' + str(cardholder["CHID"]) + '/accessLevels/' + EntryAccessLevel, json=chAccessLevel, headers=h, params = (("callAction", False),))
        
        
        return(reply.status_code, cardholder)
        
    else:
        trace("Error: " + reply_json["Message"])
        if "ModelState" in reply_json.keys():
            for field_name in reply_json["ModelState"].keys():
                trace("%s: %s"%(field_name, ";".join(reply_json["ModelState"][field_name])))

        #writeTrace('', "Error: " + reply.json()["Message"], color='IndianRed')
        return(reply_json["Message"])


def checkCard(url, h, cardholder):

    card = None

    if cardholder["CHState"] != 0:
        return
    
    reply = requests.get(url + 'cardholders/' + str(cardholder["CHID"]) + '/cards', headers=h)
    reply = reply.json()
    trace(reply)

    if reply:
        for card in reply:
            card["CardState"] = 0
            card_update = requests.put(url + 'cards', json=card, headers=h, params = (("callAction", False),))
            #trace(card_update.json())
        return
        
    else:

        get_card = requests.get(url + f'cards',  headers=h, params = (("limit", 1),("situation", 2), ("cardType", 0)))
        get_card_json = get_card.json()
        for card in get_card_json:
            card["CardState"] = 0
            card["CardEndValidityDateTime"] = cardholder["CHEndValidityDateTime"]
            card["CHID"] = cardholder["CHID"]
            card_update = requests.post(url + f'cardholders/{cardholder["CHID"]}/cards', json=card, headers=h, params = (("callAction", False),))
            #trace(card_update.content, card_update)

def checkStatus(ativo, inativo, wxs_visits_dict, wxs_acomp_dict, cpf):
    trace(f'Checking cardholder status:')

    wxs_visit = wxs_visits_dict.get(cpf)
    wxs_acomp = wxs_acomp_dict.get(cpf)

    if inativo:
        trace(f'Status (Afastado): {inativo}')
        status = 1 # CHState = 1 >> Inativo
        return(status)
        
    elif wxs_visit:
        trace(f'Status (Com Atendimento ativo)')
        status = 9 # CHState = 2 >> Desligado
        return(status)

    elif wxs_acomp:
        trace(f'Status (Com Atendimento ativo)')
        status = 9 # CHState = 2 >> Desligado
        return(status)

    elif ativo:
        trace(f'Status (Ativo): {ativo}')
        status = 0 # CHState = 2 >> Ativo
        return(status)
    
    else:
        trace('Nenhum Status definido')
        status = 1 #  CHState = 1 >> Inativo
        return(status)


def checkAttendence(url, h, wxs_visits_dict, unimed_user, wxs_user):
    #---------------------- 
    
    wxs_visit = wxs_visits_dict.get(unimed_user["IdNumber"])

    if wxs_visit:
        if wxs_user["CHState"] != 9:

            unimed_user["CHState"] = 9
            #updateUser(url, h, wxs_user)
            return(unimed_user["CHState"])
        else:
            trace("Usuário possui um atendimento ativo. CHState = 'Em Atendimento'")
            return(unimed_user["CHState"])
    else:
        if wxs_user["CHState"] == 9:

            return(unimed_user["CHState"])
            #updateUser(url, h, wxs_user)
            #createCard(url, h, wxs_user, wxs_user["AuxText15"])

        else:
            trace("Usuário não possui um atendimento ativo.")
            return(unimed_user["CHState"])


def getComboFields(url, h, unimed_fields, wxs_comboFields_list):
   
    for field in unimed_fields.keys():
        wxs_fieldID = 'lstBDA_' + str(field)
        field_exists = False
        newComboIndex = 0

        for item in wxs_comboFields_list:
            for key1, value1 in item.items():
                if value1 == wxs_fieldID:
                    newComboIndex += 1
                    if item["strLanguage2"] == unimed_fields[field]:
                        unimed_fields[field] = item["ComboIndex"]
                        field_exists = True
            
        if not field_exists:

            servername = 'Localhost\\W_ACCESS'
            userid = 'sa'
            password = '#w_access_Adm#'
            databasename = 'W_Access'

            conn = pyodbc.connect('Driver={ODBC driver 13 for SQL Server};Server='+servername+  ';UID='+userid+';PWD='+password+';Database='+databasename) 
            combo = conn.cursor()

            combo.execute("Select MAX(ComboIndex) from CfgCHComboFields where CHType = 3 and FieldID = '" + wxs_fieldID + "'")
            for row in combo:
                trace(row[0])
                newComboIndex = int(row[0]) + 1
                
            new_comboField = { "fieldID": wxs_fieldID, "CHType": 3, "ComboIndex": newComboIndex, "strLanguage1": unimed_fields[field], \
                "strLanguage2": unimed_fields[field], "strLanguage3": unimed_fields[field], "strLanguage4": unimed_fields[field]}

            reply = requests.put(url + 'chComboFields', json=new_comboField, headers=h, params = (("callAction", False),))
            unimed_fields[field] = newComboIndex
 
    return(unimed_fields)



def getCompanies(url, h, unimed_company, wxs_companies_list):
    trace("\n* Get All Users ComboFields")

    if unimed_company:
        company = [ comp for comp in wxs_companies_list if comp["CompanyName"] == unimed_company ]

        if company:
            trace(f'Empresa ({unimed_company}) Já existe')
            companyID = company[0]["CompanyID"]
            return(companyID)
            #return(str(companyID))

        else:
            # ----------------------------------- Verifica se a empresa já foi criada nessa Execução -------------- 
            reply = requests.get(url + 'companies', headers=h, params = (("limit", '1000'),))
            wxs_companies_list = reply.json()

            company = [ comp for comp in wxs_companies_list if comp["CompanyName"] == unimed_company ]

            if company:
                trace(f'Empresa ({unimed_company}) já foi criada nesta execução da integração')
                companyID = company[0]["CompanyID"]
                return(str(companyID))

            else:
                trace(f'Empresa ({unimed_company}) não existe')

                new_company = { "CompanyName": unimed_company, "Description": "", "PartitionID": 0 }
                reply = requests.post(url + 'companies', json=new_company, headers=h, params = (("callAction", False),))
                wxs_companies_list = reply.json()
                return(str(wxs_companies_list["CompanyID"]))

    else:
        return(None)


def ativaCartao(url, h, wxs_user):
    FuncCard = requests.get(url + 'cardholders/' + str(wxs_user["CHID"])+ '/cards',headers=h)
    FuncCard_json = FuncCard.json()
    if FuncCard_json:
        print(FuncCard_json)
    for card in FuncCard_json:
        print(card["CardState"], type(card["CardState"]))
        card["CardState"] = 0 # CardState 0 = Ativo
        card["CardEndValidityDateTime"] = wxs_user["CHEndValidityDateTime"]
        print(card["CardState"], type(card["CardState"]))
        FuncCard = requests.put(url + 'cards', json=card, params = (("callAction", False),), headers=h)
        print(FuncCard)
