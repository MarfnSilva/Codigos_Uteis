# -*- coding: utf-8 # -*- 

#from WXSMainScript import main_script
from typing import no_type_check
from GenericTrace import report_exception, trace
import requests, json, traceback, sys, base64, re, os
from datetime import datetime  
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


def update_user(wxs_user):
    
    trace("\n* Cardholders - Update")
    #------------------------------------ Update End Validity ------------------------------------
    end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
    end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")

    wxs_user["CHEndValidityDateTime"] = end_validity_str

    # ---------------------------------- Update Cardholder  ----------------------------------- 
    reply = requests.put(WxsConn.waccessapi_endpoint + 'cardholders', json=wxs_user, headers=WxsConn.waccessapi_header, params=(("callAction", False),))
    if reply.status_code == requests.codes.no_content:
        trace(f"Cardholder {wxs_user['FirstName']} - update OK")
        #assign_card(wxs_user)

    else:
        trace("Error: " + reply.json()["Message"])

def createUser(import_user):

    # ---------------------------------- Create New Cardholder  ----------------------------------- 
    
    new_cardholder = None

    #------------------------------------ Set End Validity ------------------------------------
    end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
    end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")

    trace("\n* Cardholders - Create")
    new_cardholder = { "FirstName": import_user["FirstName"], "IdNumber" : import_user["IdNumber"] , "CHType": import_user["CHType"], "PartitionID": import_user["PartitionID"], "CHState" : import_user["CHState"], \
                        "AuxLst02" : import_user["AuxLst02"], "AuxText04" : import_user["AuxText04"], \
                        "CHEndValidityDateTime" : end_validity_str, "AuxText05" : import_user["AuxText05"], "AuxText06" : import_user["AuxText06"], \
                        "AuxText01" : import_user["AuxText01"], "AuxText09" : import_user["AuxText09"] } 
    
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



def associate_user_group(wxs_user, import_user):
    """ Associate Import_User to a User Group


    """
    
    print("Group")

    if not import_user["import_group"]:
        return

    else:
        reply = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/groups/{import_user["import_group"]}', headers=WxsConn.waccessapi_header, params=(("callAction", False),))
        print(reply)

            

def assign_new_card(cardholder, new_card):
    getcards = requests.get(WxsConn.waccessapi_endpoint + f'cardholders/{cardholder["CHID"]}/cards', headers=WxsConn.waccessapi_header, params=(("callAction", False),))       
    trace(f'Cards associeted: {getcards}') 
    if getcards and cardholder["CHState"] == 0:
        getcards_json = getcards.json()
        for card in getcards_json:
            unassign_card = requests.delete(WxsConn.waccessapi_endpoint + f'cardholders/{cardholder["CHID"]}/cards/{card["CardID"]}', headers=WxsConn.waccessapi_header, params=(("callAction", False),))
        
        new_card["CardState"] = 0 
        new_card["CardEndValidityDateTime"] = cardholder["CHEndValidityDateTime"]
        assign_card = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/{cardholder["CHID"]}/cards', headers=WxsConn.waccessapi_header, json=new_card, params=(("callAction", False),))
        if assign_card.status_code == requests.codes.no_content:
            trace(f'Card {card["ClearCode"]} updated')

    else:
        trace('No cards found to update')

def get_age(nasc):
    time_str = nasc
    time_dte = datetime.strptime(time_str, '%d/%m/%Y').date()
    now = datetime.now()
    idade = relativedelta(now, time_dte)
    trace(idade.years)
    return(idade.years)

def get_unid_internacao(unid):
    get_lst = requests.get(WxsConn.waccessapi_endpoint + f'chComboFields', headers=WxsConn.waccessapi_header, params=(("FieldID", "lblBDA_AuxLst04"),("CHType", 8)))
    get_lst_json = get_lst.json()

    for combo in get_lst_json:
        return(combo["ComboIndex"], combo["strLanguage2"])
        
def assign_access_level(wxs_user, all_access_levels):
    trace('Assign accesss level')
    for access_level in all_access_levels:
        if wxs_user["AuxText01"] == access_level["AccessLevelName"]:
            trace(f'Access level founded with AccessLevelID = {access_level["AccessLevelID"]} and AccessLevelName = {access_level["AccessLevelName"]}')
            assign = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/accessLevels/{access_level["AccessLevelID"]}', headers=WxsConn.waccessapi_header, json={}, params=(("callAction", False),))
            return
    # GroupID 1 = Usuários sem nivel de acesso
    set_group = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/groups/1', headers=WxsConn.waccessapi_header, params=(("callAction", False),))

def get_all_access_levels():
    try:
        ac = requests.get(WxsConn.waccessapi_endpoint + f'accessLevels', headers=WxsConn.waccessapi_header)
        ac_json = ac.json()
        return(ac_json)
    except Exception as ex:
        report_exception(ex)
         
def assign_card(wxs_user):
    #------------------------------------ Set End Validity ------------------------------------
    end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
    end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")
    
    getcards = requests.get(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/cards', headers=WxsConn.waccessapi_header, params=(("callAction", False),))       
    trace(f'check if associated cards its active') 
    getcards_json = getcards.json()
    if getcards_json and wxs_user["CHState"] == 0:
        #getcards_json = getcards.json()
        for card in getcards_json:
            if card["CardState"] != 0:
                trace(f'Card inactive founded with ClearCode = {card["ClearCode"]}. Change CardStatus to 0 (Active)')
                unassign_card = requests.delete(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/cards/{card["CardID"]}', headers=WxsConn.waccessapi_header, params=(("callAction", False),))
                card["CardState"] = 0 
                card["CardEndValidityDateTime"] = wxs_user["CHEndValidityDateTime"]
                assign_card = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/cards', headers=WxsConn.waccessapi_header, json=card, params=(("callAction", False),))
                if assign_card.status_code == requests.codes.no_content:
                    trace(f'Card {card["ClearCode"]} updated')

            elif card["CardState"] != 0:
                trace(f'Card ({card["ClearCode"]}) already active')
    elif not getcards_json and wxs_user["CHState"] == 0:
        #http://localhost/W-AccessAPI/v1/cards?limit=1&situation=2&cardType=0
        trace(f'User with no cards assigned. Get card to Assign')
        get_card = requests.get(WxsConn.waccessapi_endpoint + 'cards', headers=WxsConn.waccessapi_header, params=(("limit", 1),("situation", 2), ("cardType", 0)))
        get_card_json = get_card.json()
        for card in get_card_json:
            card["CardState"] = 0
            card["CardEndValidityDateTime"] = end_validity_str
            assign_card = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/cards', headers=WxsConn.waccessapi_header, json=card, params=(("callAction", False),))
            if assign_card.status_code == requests.codes.created:
                trace(f'Card {card["ClearCode"]} updated')

    else:
        trace('No cards found to update')