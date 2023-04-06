# coding: utf-8

from typing import no_type_check
from GenericTrace import trace
from WXSConnection import *
import requests, json, traceback, sys, base64
from datetime import datetime  
from datetime import timedelta  
import time


def assign_acces_level_to_ch_if_required(wxs_chid, access_level_id):
    reply = requests.get(WxsConn.waccessapi_endpoint + f"cardholders/{wxs_chid}/accessLevels/{access_level_id}",  headers=WxsConn.waccessapi_header)
    if reply.status_code == requests.codes.not_found:
        ch_access_level = { "CHID" : wxs_chid, "AccessLevelID": access_level_id , "AccessLevelStartValidity": None , "AccessLevelEndValidity": None}
        requests.post(WxsConn.waccessapi_endpoint + f"cardholders/{wxs_chid}/accessLevels/{access_level_id}", json=ch_access_level, headers=WxsConn.waccessapi_header, params = (("callAction", False),))


def updateUser(updated_wxs_user, unimed_user):
    
    trace("Cardholders - Update")
    updated_wxs_user["CHEndValidityDateTime"] = unimed_user["CHEndValidityDateTime"]
    # ---------------------------------- Update Cardholder  ----------------------------------- 
    reply = requests.put(WxsConn.waccessapi_endpoint + 'cardholders', json=updated_wxs_user, headers=WxsConn.waccessapi_header, params = (("callAction", False),))
    trace(reply)
    if reply.status_code == requests.codes.no_content:
        trace(f"Cardholder {updated_wxs_user['FirstName']} - update OK")

        # ---------------------------------- Update Cardholder photo -----------------------------------
        photo = requests.put(WxsConn.waccessapi_endpoint + 'cardholders/' + str(updated_wxs_user["CHID"]) + '/photos/1', files=(('photoJpegData', unimed_user["PhotoImport"]),), headers=WxsConn.waccessapi_header, params = (("callAction", False),)) 

        trace(f"Cardholder {updated_wxs_user['FirstName']} - Photo updated")
        
        # ---------------------------------- Update validade da visita -----------------------------------
        getVisit = requests.get(WxsConn.waccessapi_endpoint + 'cardholders/' + str(updated_wxs_user["CHID"]) + '/activeVisit', headers=WxsConn.waccessapi_header)
        getVisit_json = getVisit.json()

        if getVisit_json:
            #getVisit_json["VisitEnd"] = updated_wxs_user["AuxDte10"]
            #setValidityEnd = requests.put(WxsConn.waccessapi_endpoint + 'cardholders/' + str(updated_wxs_user["CHID"]) + '/activeVisit', headers=WxsConn.waccessapi_header, params = (("callAction", False),))
            
            assign_acces_level_to_ch_if_required(updated_wxs_user["CHID"], 101)
    else:
        trace("Error: " + reply.json()["Message"])

    # --------- Assign accesslevel to Cardholder if checkbox "Pendência Financeira" is disable ------------------
    exitAccessLevel(updated_wxs_user)
    ### **** Revisar para usar a função assign_access_level


def update_photo(updated_wxs_user, unimed_user):
    # ---------------------------------- Update Cardholder photo -----------------------------------
    photo = requests.put(WxsConn.waccessapi_endpoint + 'cardholders/' + str(updated_wxs_user["CHID"]) + '/photos/1', files=(('photoJpegData', unimed_user["PhotoImport"]),), headers=WxsConn.waccessapi_header, params = (("callAction", False),)) 
    trace(f"Cardholder {updated_wxs_user['FirstName']} - Photo updated | Response: {photo.reason}")
        

def createUser(unimed_user):

    # ---------------------------------- Create New Cardholder  ----------------------------------- 
    new_cardholder = None

    trace("Cardholders - Create")
    new_cardholder = { "FirstName": unimed_user["FirstName"], "CHType": 7, "IdNumber": unimed_user["IdNumber"], "PartitionID": 1, \
        "AuxText05" : unimed_user["AuxText05"], "AuxChk10" : unimed_user["AuxChk10"], \
        "AuxText15" : unimed_user["AuxText15"], "AuxChk09" : unimed_user["AuxChk09"], \
        "AuxDte10" : unimed_user["AuxDte10"], "AuxText11": unimed_user["AuxText11"], \
        "AuxText09" : unimed_user["AuxText09"], "CHEndValidityDateTime" : unimed_user["CHEndValidityDateTime"]}

    reply = requests.post(WxsConn.waccessapi_endpoint + 'cardholders', json=new_cardholder, headers=WxsConn.waccessapi_header, params = (("callAction", False),))
    reply_json = reply.json()

    if reply.status_code == requests.codes.created:
        
        trace(f'New CHID: {reply_json["CHID"]} with FirstName: {reply_json["FirstName"]}')

        cardholder = reply_json
        #createCard(reply_json, unimed_user["AuxText05"])

        # ---------------------------------- Update Cardholder photo -----------------------------------
        photo = requests.put(WxsConn.waccessapi_endpoint + 'cardholders/' + str(reply_json["CHID"]) + '/photos/1', files=(('photoJpegData', unimed_user["PhotoImport"]),), headers=WxsConn.waccessapi_header, params = (("callAction", False),)) 
        
        return(reply.status_code, cardholder)
        
    else:
        trace("Error: " + reply_json["Message"])
        if "ModelState" in reply_json.keys():
            for field_name in reply_json["ModelState"].keys():
                trace("%s: %s"%(field_name, ";".join(reply_json["ModelState"][field_name])))

        return(reply_json["Message"])

# ------------------- Start a new visit ---------------------------------------

def newVisit(wxs_user, unimed_user):
    
    trace("Liberando nova visita")
    #writeTrace(wxs_user["IdNumber"],'Visit not active. Starting new visit.', color='RoyalBlue')
    #writeTrace(wxs_user["IdNumber"],'Check card to assign:', color='RoyalBlue')

    createCard(wxs_user, unimed_user["AuxText05"])
    # Neste projeto criamos o cartão, encerramos a visita e liberamos uma nova visita com o clearCode para conseguir fazer o processo de encerramento de visita corretamente.
    

    # ------------------- Defines time of first attendance --------------

    wxs_user["AuxDte09"] = str(datetime.now())
    wxs_user["AuxText09"] = unimed_user["AuxText09"]
    reply = requests.put(WxsConn.waccessapi_endpoint + 'cardholders', json=wxs_user, headers=WxsConn.waccessapi_header, params = (("callAction", False),))
    
    if reply.status_code == requests.codes.no_content:
        trace(f"Initial Attendance Time: {wxs_user['AuxDte09']}")

    else:
        trace("Error: " )


    # ------------------- Assign Entry Access Level --------------

    assign_acces_level_to_ch_if_required(wxs_user["CHID"], 101)

    # ------------------- Starting visit ---------------------------------------

    new_visit = { "CHID":str(wxs_user["CHID"]), "VisitEnd": (str(datetime.now() + timedelta(days=100))[:-3]), "VisAuxText01":unimed_user["VisAuxText01"], "VisAuxText02":unimed_user["VisAuxText02"], \
                "ClearCode": 'Pac_' + str(unimed_user["AuxText05"]), "VisAuxChk01": unimed_user["VisAuxChk01"], "VisAuxChk02": unimed_user["VisAuxChk02"], "VisAuxTextA01": unimed_user["VisAuxTextA01"] }
    
    trace(new_visit)

    reply = requests.post(WxsConn.waccessapi_endpoint + 'cardholders/' + str(wxs_user["CHID"]) + '/activeVisit', json=new_visit, headers=WxsConn.waccessapi_header, params = (("callAction", False),)) 
    reply_json = reply.json()

    if reply.status_code == requests.codes.created:
        
        trace("New Visit started")

    else:
        trace("Error: " + reply_json["Message"])

# ------------------- Creating and Assing a new card  ---------------------------------------

def createCard(wxs_user, CodPaciente):

    card = None
    VisCard = requests.get(WxsConn.waccessapi_endpoint + 'cards', params = (("CardType", 1),("ClearCode", 'Pac_' + str(CodPaciente)))) # CardType = 1 >> Visitante
    VisCard_json = VisCard.json()

    for wxs_card in VisCard_json:
        if VisCard.status_code == requests.codes.ok:
            trace("Found Card: %s %s"%(wxs_card["CardID"], wxs_card["CardEndValidityDateTime"]))
            card = wxs_card
        elif VisCard.status_code == requests.codes.not_found:
            trace("Card not found")
        else:
            trace("Error: " + wxs_card["Message"])

    if card and card["CHID"]:
        trace("Card is assigned. Unassigning it")
        reply = requests.delete(WxsConn.waccessapi_endpoint + 'cardholders/%d/cards/%d'%(card["CHID"], card["CardID"]), json=card, headers=WxsConn.waccessapi_header, params = (("callAction", False),))
        time.sleep(0.2)
        if reply.status_code == requests.codes.no_content:
            trace("Card unassigned")
        elif reply.status_code == requests.codes.not_found:
            trace("Card not found for unassign")
        else:
            trace("Error: " + reply.json()["Message"])

    if not card:
        trace("Card - Create visitor card (CardType = 1)")
        new_card = { "ClearCode": 'Pac_' + str(CodPaciente), "CardNumber": int(CodPaciente) + 200000, "PartitionID": 0, "CardType" : 1 }
        reply = requests.post(WxsConn.waccessapi_endpoint + 'cards', json=new_card, headers=WxsConn.waccessapi_header, params = (("callAction", False),))
        reply_json = reply.json()
        if reply.status_code == requests.codes.created:
            card = reply_json
            trace("New CardID: %d"%(card["CardID"]))
        else:
            trace("Error: " + reply_json["Message"])

# --------- Check if visit is started -----

def checkVisit(wxs_user, unimed_user):
    
    #wxs_visit = wxs_visits_dict.get(unimed_user["AuxText05"])
    print(wxs_user["ActiveVisit"])
    if wxs_user["ActiveVisit"]: 
    #if wxs_visit:
        trace('Visita já esta ativa',color='YellowGreen')
        #trace(wxs_visit)
        get_visit = requests.get(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/activeVisit', headers=WxsConn.waccessapi_header)
        get_visit_json = get_visit.json()

        fields_to_compare = [ "VisAuxText01",  "VisAuxTextA02", "VisAuxText02", "VisAuxChk01", "VisAuxChk02", "VisAuxTextA01"]
        fields_with_difference = [ field for field in fields_to_compare if wxs_user["ActiveVisit"][field] != unimed_user[field] ]
        
        if fields_with_difference:
            # user has changed
            #for field in fields_with_difference:
            #    wxs_user["ActiveVisit"][field] = unimed_user[field]

            deleteVisit = requests.delete(WxsConn.waccessapi_endpoint + 'cardholders/' + str(wxs_user['CHID']) + '/activeVisit' , headers=WxsConn.waccessapi_header, params = (("callAction", False),)) 
            trace(f'Delete last visit: [{deleteVisit.reason}]')
            time.sleep(0.3)
            trace(f'Usuário: {unimed_user["FirstName"]} sofreu alterações no atendimento no campos: {str(fields_with_difference)}')
            
            newAttendance(wxs_user, unimed_user)


        else:
            trace(f'Usuário: {unimed_user["FirstName"]} não alterou o nº do atendimento.')


    else:
        trace('Sem visita ativa', color='LightSalmon')
        # ---------- Check if "Data da Alta" is expired ------
        #if DataAlta_Comp > datetime.now():
        if unimed_user["AuxDte10"]:
            trace('Visita não será liberada: Possui data de alta')

        #if DataAlta_Comp < datetime.now():
        else:
            
            trace('Liberar nova Visita')
            newVisit(wxs_user, unimed_user) 

# --------- Assign accesslevel to Cardholder if checkbox "Pendência Financeira" (Financial Pending) is disable -----------------------

def exitAccessLevel(wxs_user):
    ExitAccessLevel = 100 # Testes
    trace(f'unimed_pend_financ: {wxs_user["AuxChk10"]} \npend_Alta: {wxs_user["AuxChk09"]}')
    if wxs_user["AuxChk10"] == False and wxs_user["AuxChk09"] == False and wxs_user["AuxDte10"]:
        trace(f'CurrentUser CHID: {wxs_user["CHID"]} user has permission to leave.')
        assign_acces_level_to_ch_if_required(wxs_user["CHID"], ExitAccessLevel)
    else:
        trace(f'CurrentUser CHID: {wxs_user["CHID"]} has financial pending')
        DelAccessLevel = requests.delete(WxsConn.waccessapi_endpoint + f'cardholders/{wxs_user["CHID"]}/accessLevels/{ExitAccessLevel}', headers=WxsConn.waccessapi_header, params = (("callAction", False),))
        time.sleep(0.2)
# ------------------- Start a new attendance ---------------------------------------

def newAttendance(wxs_user, unimed_user):
    
    new_attendance = { 
        "CHID":str(wxs_user["CHID"]), 
        "VisitStart": (str(datetime.now() + timedelta(seconds=2))[:-3]), 
        "VisitEnd": (str(datetime.now() + timedelta(days=100))[:-3]), 
        "VisAuxText01":unimed_user["VisAuxText01"], 
        "VisAuxText02":unimed_user["VisAuxText02"], 
        "ClearCode": 'Pac_' + str(unimed_user["AuxText05"]), 
        "VisAuxChk01": unimed_user["VisAuxChk01"], 
        "VisAuxChk02": unimed_user["VisAuxChk02"], 
        "VisAuxTextA01": unimed_user["VisAuxTextA01"], 
        "VisAuxTextA02": unimed_user["VisAuxTextA02"] }
 
    trace(f'new_attendance: {new_attendance}')

    reply = requests.post(WxsConn.waccessapi_endpoint + 'cardholders/' + str(wxs_user["CHID"]) + '/activeVisit', json=new_attendance, headers=WxsConn.waccessapi_header, params = (("callAction", False),)) 
    reply_json = reply.json()

    if reply.status_code == requests.codes.created:
        
        trace("Cardholder updated with new attendance")
        trace(f'Novo atendimento: {new_attendance["VisAuxText01"]}')
        assign_acces_level_to_ch_if_required(wxs_user["CHID"], 101)
        update_photo(wxs_user, unimed_user)

    else:
        trace("Error: " + reply_json["Message"])

# ------------------- Change cardState if user is set to active ---------------------------------------

def updateCard(ClearCode):
        
    reply = requests.get(WxsConn.waccessapi_endpoint + 'cards', headers=WxsConn.waccessapi_header, params = (("ClearCode", ClearCode),))
    wxs_card = reply.json()
    
    wxs_card["CardState"] = 0
    wxs_card["CardEndValidityDateTime"] = (datetime.now() + timedelta(days=100)).strftime("%Y-%m-%d %H:%M:%S")       
    data = wxs_card["CardEndValidityDateTime"]
   
    reply = requests.put(WxsConn.waccessapi_endpoint + 'cards', json=wxs_card, headers=WxsConn.waccessapi_header, params = (("callAction", False),))
    trace(reply.content)
    if reply.status_code == requests.codes.no_content:
        trace(f"Card {ClearCode} - update OK \nValidade Cartão: {data}")

    else:
        trace("Error: " + reply.json()["Message"])

def users_with_difference(conn, current_set, first_iteration):

    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    cursor = conn.cursor()
    cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI' NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'")

    script = f"SELECT cod_atend, cod_pac, nm_paciente, NR_CPF, RG, DS_Leito, \
                    DT_ALTA, TIPO_ATEND, DS_UNID_INT, COD_EMPRESA, NM_EMPRESA, \
                    SN_MENOR_IDADE, PEND_FINAN, PEND_ALTA, DS_UNID_INT, ISOLAMENTO, LIB_VIS, JUST_LIB_VIS, ultima_atualiza_cad \
                    FROM DBAMV.VDIC_UVS_CATRACA_PAC_SEMFOTO where dt_alta is null \
                    or dt_alta > '{start_date}'"

    trace('Reading users in client View...', color='DeepSkyBlue')
    cursor.execute(script)
    select = cursor.fetchall()
    new_set = set([ tuple(x) for x in select])
    changed_users = new_set - current_set

    changed_lst = []
    changed_ids = None
    if changed_users:
        for user in changed_users:
            changed_lst.append(str(user[1]))
        changed_ids = "'" + "','".join(map(str, changed_lst)) + "'"

    dump_initial = WxsConn.dump_initial_iteration
    if dump_initial and first_iteration:
        trace('First Iteration and Dump users [True], ignoring users.', color='Goldenrod')
        changed_ids = None
        changed_users = set()
        return(changed_ids, changed_users, new_set)
    else:
        return(changed_ids, changed_users, new_set)

