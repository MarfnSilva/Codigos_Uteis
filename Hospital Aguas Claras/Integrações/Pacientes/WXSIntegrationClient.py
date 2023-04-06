# -*- coding: utf-8 # -*- 

#from WXSMainScript import main_script
from typing import no_type_check
from GenericTrace import trace
import requests, json, traceback, sys, base64, re, os, pyodbc
from datetime import datetime  
#import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta  
from requests.models import Response
import time
from WXSConnection import *

def assign_acces_level_to_ch_if_required(wxs_chid, access_level_id):
    reply = requests.get(WxsConn.waccessapi_endpoint + f"cardholders/{wxs_chid}/accessLevels/{access_level_id}",  headers=WxsConn.waccessapi_header, params=(("callAction", False),))
    if reply.status_code == requests.codes.not_found:
        ch_access_level = { "CHID" : wxs_chid, "AccessLevelID": access_level_id , "AccessLevelStartValidity": None , "AccessLevelEndValidity": None}
        requests.post(WxsConn.waccessapi_endpoint + f"cardholders/{wxs_chid}/accessLevels/{access_level_id}", json=ch_access_level, headers=WxsConn.waccessapi_header, params=(("callAction", False),))


def update_user(updated_wxs_user, import_user):
    trace("Cardholders - Update")
    #------------------------------------ Update End Validity ------------------------------------
    updated_wxs_user["CHEndValidityDateTime"] = import_user["EndValidity"] 
    #updated_wxs_user["CHState"] = 0
    # ---------------------------------- Update Cardholder  ----------------------------------- 
    reply = requests.put(WxsConn.waccessapi_endpoint + 'cardholders', json=updated_wxs_user, headers=WxsConn.waccessapi_header, params=(("callAction", False),))
    trace(reply)
    if reply.status_code == requests.codes.no_content:
        trace(f"Cardholder {updated_wxs_user['FirstName']} - update OK")
    else:
        trace("Error: " + reply.json()["Message"])

def create_user(import_user):
    # ---------------------------------- Create New Cardholder  ----------------------------------- 
    new_cardholder = None
    
    trace("Cardholders - Create")
    new_cardholder = { "FirstName": import_user["FirstName"], "CHType": import_user["CHType"], "PartitionID": import_user["PartitionID"], "CHState" : 0, \
                        "AuxLst03" : import_user["AuxLst03"], "AuxText05" : import_user["AuxText05"], "IdNumber" : import_user["IdNumber"], "AuxLst04" : import_user["AuxLst04"], \
                        "CHEndValidityDateTime" : import_user["EndValidity"], "AuxText13" : import_user["AuxText13"], "AuxText11" : import_user["AuxText11"], \
                        "AuxLst05" : import_user["AuxLst05"], "AuxText15" : import_user["AuxText15"], "AuxText07" : import_user["AuxText07"] ,"AuxDte01" : import_user["AuxDte01"], \
                        "AuxChk04" : import_user["AuxChk04"], "AuxLst02" : import_user["AuxLst02"] } 
    
    trace(new_cardholder)
    reply = requests.post(WxsConn.waccessapi_endpoint + 'cardholders', json=new_cardholder, headers=WxsConn.waccessapi_header, params=(("callAction", False),))
    reply_json = reply.json()

    if reply.status_code == requests.codes.created:
        trace(f'New CHID: {reply_json["CHID"]} with FirstName: {reply_json["FirstName"]}')

        cardholder = reply_json
        return(reply.status_code, cardholder)
        
    else:
        trace("Error: " + reply_json["Message"])
        if "ModelState" in reply_json.keys():
            for field_name in reply_json["ModelState"].keys():
                trace("%s: %s"%(field_name, ";".join(reply_json["ModelState"][field_name])))

        return(reply_json["Message"])


# ------------------- Creating and Assing a new card  ---------------------------------------

def check_card(wxs_user):
    """ Check if user has a card assing. 
            > If card doesn't assing: check if this card exists and assing to user.
            > If card doesn't exist: Create a new card and assing to user.

    Args:
    :param url: Url
    :param h: Url
    :param cardholder: 
    :param import_user:

    """
    trace('Cheking card')
    card = None

    if wxs_user["CHState"] != 0:
        trace(f'Condition: CHState = {wxs_user["CHState"]} AND CHType = {wxs_user["CHType"]} : Return False')
        return(False)

    trace('Check if card exists')

    if wxs_user["Cards"]:
        for card in wxs_user["Cards"]:
            if card["CardState"] != 0:
                card["CardEndValidityDateTime"] = wxs_user["CHEndValidityDateTime"]
                card["CardState"] = 0
                set_card = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/cards', headers=WxsConn.waccessapi_header, json=card, params=(("callAction", False),))
                return()
     
# --------- Assign accesslevel to Cardholder if checkbox "Pendência Financeira" (Financial Pending) is disable -----------------------

def exitAccessLevel(wxs_user):
    ExitAccessLevel = 100 # Testes
    if wxs_user["AuxChk10"] == False and wxs_user["AuxChk09"] == False and wxs_user["AuxDte10"]:
        trace(f'CurrentUser CHID: {wxs_user["CHID"]} user has permission to leave.')
        assign_acces_level_to_ch_if_required(wxs_user["CHID"], ExitAccessLevel)
    else:
        trace(f'CurrentUser CHID: {wxs_user["CHID"]} has financial pending')
        DelAccessLevel = requests.delete(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/accessLevels/{ExitAccessLevel}', headers=WxsConn.waccessapi_header, params=(("callAction", False),))


def create_card(new_card):
    trace(f'Creating new card.')
    create_card = requests_post('cards', json=new_card)
    card = create_card.json()
    if card:
        trace(f'Card created with cardID = {card["CardID"]}')
        return(card)
    else:
        trace(f'Error creating card with clearcode = {new_card["ClearCode"]}')


def check_card(wxs_user):
    card_name = str(wxs_user["CHID"])
    card_name = f'PAC_2{card_name.zfill(8)}' 
    new_card = { "ClearCode": card_name, "CardNumber": wxs_user["CHID"] + 200000000, "FacilityCode": 0, "CardType": 1, "PartitionID": 0, "IsAutomaticCard": True }
    get_card = requests_get('cards', params=(("limit", 1),("ClearCode", card_name)))
    get_card_json = get_card.json()
    if not get_card_json:
        card = create_card(new_card)
    else:
        for cd in get_card_json:
            card = cd
            pass
    return(card)

def get_age(nasc):
    time_str = nasc
    time_dte = datetime.strptime(time_str, '%d/%m/%Y').date()
    now = datetime.now()
    idade = relativedelta(now, time_dte)
    trace(idade.years)
    return(idade.years)

def get_unid_internacao(unid):
    get_lst = requests.get(WxsConn.waccessapi_endpoint + f'chComboFields', headers=WxsConn.waccessapi_header, params=(("FieldID", "lstBDA_AuxLst04"),("CHType", 8)))
    get_lst_json = get_lst.json()

    for combo in get_lst_json:
        if combo["strLanguage2"] == unid:
            return(combo["ComboIndex"])

def get_all_access_levels():
    ac = requests.get(WxsConn.waccessapi_endpoint + f'accessLevels', headers=WxsConn.waccessapi_header)
    ac_json = ac.json()
    return(ac_json)

def check_attendance(wxs_user, import_user):
    if wxs_user["ActiveVisit"]:
        if wxs_user["ActiveVisit"]["VisAuxText01"] == import_user["VisAuxText01"]:
            return(True)
        else:
            return(False)
    else:
        return(False)

# ------------------- Start a new attendance ---------------------------------------
def new_attendence(wxs_user, import_user, card):
    if wxs_user["ActiveVisit"]:
        del_visit = requests.delete(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/activeVisit', headers=WxsConn.waccessapi_header, params=(("callAction", False),))
    
    new_visit_obj = {
            "CHID": wxs_user["CHID"],
            "FirstName": wxs_user["FirstName"],
            "ClearCode": card["ClearCode"],
            "VisitEnd": import_user["EndValidity"],
            "OperName": "integra_atend",
            "VisAuxText01": import_user["VisAuxText01"]
            }

    new_att = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/activeVisit', headers=WxsConn.waccessapi_header, json=new_visit_obj, params=(("callAction", False),))

    if new_att.status_code == requests.codes.created:
        trace("Cardholder updated with new attendance")
        trace(f'Novo atendimento: {new_visit_obj["VisAuxText01"]}')
        #update_user(wxs_user, import_user)
        
    else:
        trace("Error creating new attendence")
        trace("Error: " + new_att.json()["Message"])

def set_status(import_user_lst):
    # Tuple: (AuxLst05, EndValidity)
    
    # Ativo
    if not import_user_lst["tipo_saida"]:
        end_validity = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d %H:%M:%S")
        return(0, end_validity)

    elif import_user_lst["tipo_saida"].upper() == 'ALTA':
        end_validity = (datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
        return(1, end_validity)

    elif import_user_lst["tipo_saida"].upper() == 'OBITO':
        end_validity = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        return(2, end_validity)
    
    elif import_user_lst["tipo_saida"].upper() == 'INTERNACAO' or import_user_lst["tipo_saida"].upper() == 'INTERNAÇÃO':
        end_validity = (datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")
        return(3, end_validity)
    else:
        end_validity = (datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
        return(None, end_validity)

def set_cpf_mask(cpf):
    if cpf:
        cpf_mask = cpf.replace('.','').replace('-','') # 12345678900
        if len(cpf_mask) < 11:
            cpf_mask = cpf_mask.zfill(11)
        cpf_mask = '{}.{}.{}-{}'.format(cpf_mask[:3], cpf_mask[3:6], cpf_mask[6:9], cpf_mask[9:])
        return(cpf_mask)
    else:
        return(None)

def get_nasc(data_nasc):
    data_saida = datetime.strptime(data_nasc, '%d/%m/%Y').strftime('%Y-%m-%d 00:00:00')
    return(data_saida)


def assign_access_level_contact(wxs_user):
    unid_internacao = wxs_user["AuxLst04"]
    get_combo = requests.get(WxsConn.waccessapi_endpoint + f'chComboFields', params=(("CHType", 8),("fieldID", "lstBDA_AuxLst04"),("comboIndex", unid_internacao)),  headers=WxsConn.waccessapi_header)
    get_combo_json = get_combo.json()

    for item in get_combo_json:
        unid_internacao_dsc = item["strLanguage2"]
        continue

    get_access = requests.get(WxsConn.waccessapi_endpoint + f'accessLevels', headers=WxsConn.waccessapi_header)
    get_access_json = get_access.json()

    for access in get_access_json:
        if access["AccessLevelName"] == unid_internacao_dsc:
            access_level_id = access["AccessLevelID"]
            continue

    conn = False 
    conn = sql_connect(conn)
    script = f'SELECT CHID FROM CHActiveVisits WHERE ContactCHID = {wxs_user["CHID"]}'
    getcontact = conn.cursor()
    getcontact.execute(script)
    for visitor in getcontact:
        get_vis = requests.get(WxsConn.waccessapi_endpoint + f'cardholders/{visitor[0]}', params=(("includeTables", "CHAccessLevels"),("fields", "CHID,FirstName,CHAccessLevels")))
        get_vis_json = get_vis.json()
        for vis in get_vis_json["CHAccessLevels"]:
            del_accesslelve = requests.delete(WxsConn.waccessapi_endpoint + f'cardholders/{visitor[0]}/accessLevels/{vis["AccessLevelID"]}', headers=WxsConn.waccessapi_header)
        assign_access = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/{visitor[0]}/accessLevels/{access_level_id}',headers=WxsConn.waccessapi_header, json={})
        trace(f'AccessLevel assign return = {assign_access.reason}')            


def assign_access_level(wxs_user):
    unid_internacao = wxs_user["AuxLst04"]
    get_combo = requests.get(WxsConn.waccessapi_endpoint + f'chComboFields', params=(("CHType", 8),("fieldID", "lstBDA_AuxLst04"),("comboIndex", unid_internacao)),  headers=WxsConn.waccessapi_header)
    get_combo_json = get_combo.json()

    for item in get_combo_json:
        unid_internacao_dsc = item["strLanguage2"]
        continue

    for access in wxs_user["CHAccessLevels"]:
            del_accesslelve = requests.delete(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/accessLevels/{access["AccessLevelID"]}', headers=WxsConn.waccessapi_header)
            trace(f'Deleting current accessLevelID = {access["AccessLevelID"]} | response = {del_accesslelve.reason}')
    
    get_access = requests.get(WxsConn.waccessapi_endpoint + f'accessLevels', headers=WxsConn.waccessapi_header)
    get_access_json = get_access.json()

    for access in get_access_json:
        if access["AccessLevelName"] == unid_internacao_dsc:
            access_level_id = access["AccessLevelID"]
            assign_access = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/accessLevels/{access_level_id}',headers=WxsConn.waccessapi_header, json={})
            trace(f'AccessLevel assign return = {assign_access.reason}')            
            continue