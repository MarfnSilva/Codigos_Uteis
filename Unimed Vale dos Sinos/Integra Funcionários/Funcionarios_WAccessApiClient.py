# coding: utf-8

import requests, json, traceback, sys, base64
from datetime import datetime  
from datetime import timedelta  
from GenericTrace import trace, report_exception
from WXSConnection import *
import pyodbc


def assign_acces_level_to_ch_if_required(url, h, wxs_chid, access_level_id):
    reply = requests_get(f"cardholders/{wxs_chid}/accessLevels/{access_level_id}")
    if reply.status_code == requests.codes.not_found:
        ch_access_level = { "CHID" : wxs_chid, "AccessLevelID": access_level_id , "AccessLevelStartValidity": None , "AccessLevelEndValidity": None}
        requests_post(f"cardholders/{wxs_chid}/accessLevels/{access_level_id}", json=ch_access_level )


def updateUser(url, h, updated_wxs_user):
  
    # ---------------------------------- Update Cardholder  ----------------------------------- 

    trace('Cardholders - Update', updated_wxs_user["IdNumber"], color='DarkOrange')
        
    #--------- update cardholder validity -----------
    now = datetime.now() + timedelta(days=3600)
    updated_wxs_user["CHEndValidityDateTime"] = now.strftime("%Y-%m-%dT%H:%M:%S")

    reply = requests_put('cardholders', json=updated_wxs_user)
    
    if reply.status_code == requests.codes.no_content:
        trace(f"Cardholder {updated_wxs_user['FirstName']} - update OK")
        trace(updated_wxs_user["IdNumber"], f"Cardholder {updated_wxs_user['FirstName']} - update OK", color='DarkOrange')

        # ------------------- Assign Entry Access Level --------------
        EntryAccessLevel = 98 # Produção
        assign_acces_level_to_ch_if_required(url, h, updated_wxs_user["CHID"], EntryAccessLevel)
        # chAccessLevel = { "CHID": str(updated_wxs_user["CHID"]), "AccessLevelID": EntryAccessLevel , "AccessLevelStartValidity":str(datetime.now()), "AccessLevelEndValidity": updated_wxs_user["CHEndValidityDateTime"]}
        # AddAccessLevel = requests.post(url + 'cardholders/' + str(updated_wxs_user["CHID"]) + '/accessLevels/' + EntryAccessLevel, json=chAccessLevel, headers=h ,params =(("callAction", False),))
        
        
    else:
        trace("Error: " + reply.json()["Message"], updated_wxs_user, color='IndianRed')


def createUser(url, h, unimed_user):

    # ---------------------------------- Create New Cardholder  ----------------------------------- 
    
    new_cardholder = None

    trace("Cardholders - Create")
    new_cardholder = {"FirstName": unimed_user["FirstName"], "CHType": 2, "IdNumber": unimed_user["IdNumber"], "PartitionID": 1,
                      "AuxText15": unimed_user["AuxText15"], "AuxText14": unimed_user["AuxText14"], "AuxLst01": unimed_user["AuxLst01"],
                      "AuxLst02": unimed_user["AuxLst02"], "AuxLst03": unimed_user["AuxLst03"], "AuxLst05": unimed_user["AuxLst05"], "AuxText10": unimed_user["AuxText10"],
                      "AuxDte04": unimed_user["AuxDte04"], "AuxDte05": unimed_user["AuxDte05"], "AuxDte06": unimed_user["AuxDte06"], "AuxDte07": unimed_user["AuxDte07"],
                      "AuxDte08": unimed_user["AuxDte08"], "AuxDte09": unimed_user["AuxDte09"]}
    #new_cardholder["CHState"] = checkStatus(unimed_user) ## Check Unimed status to define CHState

    reply = requests_post('cardholders', json=new_cardholder)
    reply_json = reply.json()

    if reply.status_code == requests.codes.created:
        trace(f'New CHID: {reply_json["CHID"]} with FirstName: {reply_json["FirstName"]}', unimed_user["IdNumber"], color='DarkGreen')

        cardholder = reply_json
        #createCard(url, h, cardholder, unimed_user["AuxText15"])

        # ------------------- Assign Entry Access Level --------------
        EntryAccessLevel = 98 # Produção
        assign_acces_level_to_ch_if_required(url, h, cardholder["CHID"], EntryAccessLevel)

        # EntryAccessLevel = '98' # Produção
        # chAccessLevel = { "CHID": str(cardholder["CHID"]), "AccessLevelID": EntryAccessLevel , "AccessLevelStartValidity":str(datetime.now()), "AccessLevelEndValidity": cardholder["CHEndValidityDateTime"]}
        # AddAccessLevel = requests.post(url + 'cardholders/' + str(cardholder["CHID"]) + '/accessLevels/' + EntryAccessLevel, json=chAccessLevel, headers=h, params =(("callAction", False),))
        
        
        return(reply.status_code, cardholder)
        
    else:
        write_txt(f'**** verificar usuário no RM ou ID_Import: CPF: {new_cardholder["IdNumber"]} | Nome: {new_cardholder["FirstName"]} ******')

        trace("Error: " + reply.json()["Message"], color='IndianRed')
        return(reply_json["Message"])


def createCard(url, h, cardholder):

    card = None

    if cardholder["CHState"] != 0:
        return
    
    reply = requests_get('cardholders/' + str(cardholder["CHID"]) + '/cards')
    reply = reply.json()
    trace(reply)

    if reply:
        for card in reply:
            card["CardState"] = 0
            card_update = requests_put('cards', json=card)
            #trace(card_update.json())
        return

    else:
        get_card = requests_get('cards', params = (("situation", '2'), ("limit", 1), ("cardType", 0)) )
        get_card_json = get_card.json()
        if get_card_json:
            card = get_card_json[0]
            #print(get_card_json)
            card["CardState"] = 0
            card["CHID"] = cardholder["CHID"]
            card_update = requests_post( f'cardholders/{cardholder["CHID"]}/cards', json=card)
            trace(card_update.content)
        else:
            trace("nenhum cartão disponível no sistema")
   

def checkStatus(admissao, demissao, ferias, afastamento, wxs_visits_dict, wxs_acomp_dict, cpf):
    trace(f'Checking cardholder status:')

    wxs_visit = wxs_visits_dict.get(cpf)
    wxs_acomp = wxs_acomp_dict.get(cpf)

    if cpf == '03613608006':
        print('teste')
    if wxs_visit:
        trace(f'Status (Com Atendimento ativo)')
        status = 9 # CHState = 2 >> Em Atendimento
        return(status)

    elif wxs_acomp:
        trace(f'Status (Com Atendimento ativo)')
        status = 9 # CHState = 2 >> Em Atendimento
        return(status)

    elif demissao:
        trace(f'Status (Demitido): {demissao}')
        status = 2 # CHState = 2 >> Desligado
        return(status)
    
    elif afastamento:
        trace(f'Status (Afastado): {afastamento}')
        status = 4 # CHState = 4 >> Afastamento
        return(status)
    
    elif ferias:
        trace(f'Status (Ferias): {ferias}')
        status = 3 # CHState = 3 >> Ferias
        return(status)

    elif admissao:
        trace(f'Status (Normal): {admissao}')
        status = 0 # CHState = 0 >> Ativo
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

            combo.execute("Select MAX(ComboIndex) from CfgCHComboFields where CHType = 2 and FieldID = '" + wxs_fieldID + "'")
            for row in combo:
                trace(row[0])
                newComboIndex = int(row[0]) + 1
                
            new_comboField = { "fieldID": wxs_fieldID, "CHType": 2, "ComboIndex": newComboIndex, "strLanguage1": unimed_fields[field], \
                "strLanguage2": unimed_fields[field], "strLanguage3": unimed_fields[field], "strLanguage4": unimed_fields[field]}

            reply = requests_put('chComboFields', json=new_comboField)
            unimed_fields[field] = newComboIndex
 
    return(unimed_fields)



def getCompanies(url, h, unimed_company, wxs_companies_list):
    trace("Get All Users ComboFields")

    if unimed_company:
        company = [ comp for comp in wxs_companies_list if comp["CompanyName"] == unimed_company ]

        if company:
            trace(f'Empresa ({unimed_company}) Já existe')
            companyID = company[0]["CompanyID"]
            return(companyID)
            #return(str(companyID))

        else:
            # ----------------------------------- Verifica se a empresa já foi criada nessa Execução -------------- 
            reply = requests_get('companies')
            wxs_companies_list = reply.json()

            company = [ comp for comp in wxs_companies_list if comp["CompanyName"] == unimed_company ]

            if company:
                trace(f'Empresa ({unimed_company}) já foi criada nesta execução da integração')
                companyID = company[0]["CompanyID"]
                return(str(companyID))

            else:
                trace(f'Empresa ({unimed_company}) não existe')

                new_company = { "CompanyName": unimed_company, "Description": "", "PartitionID": 0 }
                reply = requests_post( 'companies', json=new_company)
                wxs_companies_list = reply.json()
                return(str(wxs_companies_list["CompanyID"]))

    else:
        return(None)
