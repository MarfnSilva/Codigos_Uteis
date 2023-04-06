# -*- coding: utf-8 -*- 

#import cx_Oracle
import pyodbc, requests, json, traceback, sys
from datetime import datetime  
from datetime import timedelta 
from GenericTrace import trace
from Acomp_WAccessApiClient import *
from WXSConnection import *
import time

def lock_cardholders_with_pendency(conn):
    try:
        trace('------ Inicio da Integração -------', color='OrangeRed')
        ## ----------------------------------Cursor to remove AccessLevels ---------------------------
        DelAccessLevels = conn.cursor()
        DelAccessLevels.execute("Select CHLastTransit.CHID, AccessLevelID, AccessLevelStartValidity, \
                        CHAuxContactCH.AuxChk10, CHAuxContactCH.AuxChk09, acomp.FirstName, contact.FirstName, CHAuxContactCH.AuxChk07, \
                        contact.CHID, CHAuxUser.AuxTextA05 from CHLastTransit \
                        Left JOIN CHMAin acomp on acomp.CHID = CHLastTransit.CHID \
                        JOIN CHAccessLevels on CHAccessLevels.CHID = CHLastTransit.CHID \
                        LEFT JOIN CHActiveVisits ON CHActiveVisits.CHID = acomp.CHID \
                        JOIN CHAux CHAuxContactCH ON CHActiveVisits.ContactCHID = CHAuxContactCH.CHID \
                        JOIN CHAux CHAuxUser ON acomp.CHID = CHAuxUser.CHID \
                        Left JOIN CHMAin contact on CHActiveVisits.ContactCHID = contact.CHID \
                        where ZoneID not in (2, 0) AND acomp.CHType = 1 \
                        and (CHAuxContactCH.AuxChk10 = 1 OR CHAuxContactCH.AuxChk09 = 1 OR CHAuxContactCH.AuxDte10 is null) \
                        AND CHActiveVisits.VisAuxChk01 = 0 AND CHActiveVisits.VisAuxLst02 = 2")

        # ZoneID in (2,0) >> Zonas externas do hospital. O acompanhante será verificado somente se estiver nas zonas internas do hospital.
        # acomp.CHType = 8 >> Usuário do tipo "Acompanhante"
        # CHAuxContactCH.AuxChk03 = 1 >> Verifica se paciente é menor de idade
        # CHAuxContactCH.AuxChk10 = 1 >> Verifica se paciente possui alguma pendencia financeira OU
        # CHAuxContactCH.AuxChk09 = 1 >> Verifica se paciente possui alguma pendencia de alta

        if DelAccessLevels.rowcount == 0:
            trace('Nenhum usuário para remover o nível de acesso.', color='salmon')

        for wxs_chid,accesslevelID,startValidityAccessLevel,pend_financ,pend_alta,wxs_Firstname,wxs_ContactName,contactUpdated,contactCHID,accesslevelDeactivated in DelAccessLevels:
            trace(f'CHID = {wxs_chid} Tirar o nivel', color='salmon')

            reply = requests_get(f'cardholders/{wxs_chid}')
            cardholder = reply.json()
            if reply.status_code != requests.codes.ok:
                trace(f'HTTP reply error: {reply.status_code} - {reply.text}', color='salmon')
                return

            removed_access_level_lst = read_local_db(wxs_chid)
            removed_access_level_lst = None if removed_access_level_lst == 'None' else removed_access_level_lst
            if removed_access_level_lst:
                removed_access_level_lst = removed_access_level_lst.split(",")
                removed_access_level_lst.append(accesslevelID)
                removed_access_level = str(removed_access_level_lst).replace('[', '').replace(']', '').replace("'", "").replace(' ', '').replace('None','')
                write_local_db(wxs_chid, removed_access_level)
            
            else:
                removed_access_level_lst = accesslevelID
                write_local_db(wxs_chid, removed_access_level_lst)

            trace(f'Lista: {str(removed_access_level_lst)}', wxs_chid, color='salmon')

            contents = cardholder["AuxTextA01"]
            trace(contents, wxs_chid, color='salmon')
            warning_text = '>>>> Saída do responsável bloqueada por pendências do paciente <<<<\n'
            if contents:
                if warning_text in contents:
                    pass
                else:
                    cardholder["AuxTextA01"] = warning_text + cardholder["AuxTextA01"]
            else:
                    cardholder["AuxTextA01"] = warning_text
            
            reply = requests_put('cardholders', json=cardholder)
            trace(reply, wxs_chid,  color='salmon')
            if reply.status_code == requests.codes.no_content:
                trace(f"Cardholder {cardholder['FirstName']} - update OK", wxs_chid)
            else:
                trace("Error: " + reply.json()["Message"], wxs_chid, color='salmon')
            
            DelAccessLevel = requests_delete(f'cardholders/{wxs_chid}/accessLevels/{accesslevelID}')
            trace(f'O usuario {wxs_Firstname} teve o acesso de saida bloqueado pois seu contato: {wxs_ContactName} possui alguma restricao', wxs_chid, color = 'salmon')
    except Exception as ex:
        report_exception(ex)


def reactivate_cardholders(conn):
    try:
        ## ----------------------------------Cursor to Add AccessLevels ---------------------------
        ADDAccessLevels = conn.cursor()
        ADDAccessLevels.execute("Select CHMainAcomp.CHID, CHMainAcomp.FirstName, ContactCHID \
                                FROM CHActiveVisits \
                                JOIN CHMain CHMainAcomp ON CHMainAcomp.CHID = CHActiveVisits.CHID \
                                JOIN CHAux CHAuxAcomp ON CHAuxAcomp.CHID = CHMainAcomp.CHID \
                                JOIN CHAux CHAuxContactCH ON CHAuxContactCH.CHID = CHActiveVisits.ContactCHID \
                                WHERE CHMainAcomp.CHType = 1 \
                                AND ((CHActiveVisits.VisAuxChk01 = 1) \
                                OR (CHAuxContactCH.AuxChk09 = 0 AND CHAuxContactCH.AuxChk10 = 0 AND CHAuxContactCH.AuxDte10 IS NOT NULL)) \
                                AND CHMainAcomp.CHID not in (SELECT CHID FROM CHAccessLevels where chid = CHMainAcomp.CHID)")
                                
        # CHMainAcomp.CHType = 1 >> Verifica se usuários é do tipo acompanhante
        # CHAuxContactCH.AuxChk10 = 0 >> Contato da visita não possui pendencia financeira
        # CHAuxContactCH.AuxChk09 = 0 >> Contato da visita nâo possui nenhuma pendencia de alta
        # CHAuxAcomp.AuxChk03 = 1 >> CheckBox para liberação manual do Responsávels

        if ADDAccessLevels.rowcount == 0:
            trace('Nenhum usuário para receber o nível de acesso')
            
        for wxs_chid, firstname, wxs_ContactName in ADDAccessLevels:
            removed_access_levels = read_local_db(wxs_chid)
            removed_access_levels = None if removed_access_levels == 'None' else removed_access_levels
            if removed_access_levels:
                trace(wxs_chid, f'O usuário {firstname} possui permissão para receber os níveis de acesso que foram removidos', color='lightgreen')
                trace((type(removed_access_levels), removed_access_levels), color='lightgreen')
                removed_access_level_lst = removed_access_levels.split(",")
                for ral in removed_access_level_lst:
                    trace(ral, color='lightgreen')
                    chAccessLevel = { "CHID" : wxs_chid, "AccessLevelID": int(ral)}
                    add = requests_post(f'cardholders/{wxs_chid}/accessLevels/{ral}', json=chAccessLevel)
                    trace(f'O usuario {firstname} recebeu o nível de acesso ID: {ral} pois seu contato CHID = {wxs_ContactName} não possui mais nenhuma pendencia.', color='lightgreen')
                
                reply = requests_get(f'cardholders/{wxs_chid}')
                cardholder = reply.json()
                contents = cardholder["AuxTextA01"]
                warning_text = '>>>> Saída do responsável bloqueada por pendências do paciente <<<<'
                if contents:
                    if warning_text in contents:
                        cardholder["AuxTextA01"] = cardholder["AuxTextA01"].replace(warning_text, '')
                    else:
                        continue

                write_local_db(wxs_chid, None)
                reply = requests_put('cardholders', json=cardholder) 
            else:
                trace('No Access Level to remove')
                
    except Exception as ex:
        report_exception(ex)

def check_fornecedor():
    try:        
        #---------------------------------------------------------------------------------------------------------------------
        # Tratamento dos Fornecedores para bloquear o CHType 6 caso exista uma visita ativa (CHType 1)
        #
        # ---------------------------------- Get all users in W-Access DB -----------------------------------
        trace("Bloquear fornecedores com visita ou atendimento ativo")

        reply = requests_get('cardholders', params = (("CHType", '6'),("limit", '20000')))
        wxs_users_list = reply.json()

        # ---------------------------------- Get all Active Visits in W-Access -----------------------------------
        reply = requests_get('cardholders/searchGeneric', params = (("filter.cHType", '7'),("filter.startedVisits", True)))
        if reply.status_code != requests.codes.ok:
            trace(f'*** HTTP reply error:{reply.status_code} - {reply.reason}', color='salmon')
            return

        wxs_visits_list = reply.json()
        reply = requests_get('cardholders/searchGeneric', params = (("filter.cHType", '1'),("filter.startedVisits", True)))
        if reply.status_code != requests.codes.ok:
            trace(f'*** HTTP reply error: {reply.status_code} - {reply.reason}', color='salmon')
            return
        wxs_acomp_list = reply.json()

        wxs_users_dict = {}
        for wxs_user in wxs_users_list:
            if wxs_user["IdNumber"]:
                wxs_users_dict[wxs_user["IdNumber"].replace(".", "").replace("-","")] = wxs_user

        wxs_visits_dict = {}
        for wxs_visit in wxs_visits_list:
            if wxs_visit["IdNumber"]:
                wxs_visits_dict[wxs_visit["IdNumber"].replace(".", "").replace("-","")] = wxs_visit

        wxs_acomp_dict = {}
        for wxs_acomp in wxs_acomp_list:
            if wxs_acomp["IdNumber"]:
                wxs_acomp_dict[wxs_acomp["IdNumber"].replace(".", "").replace("-","")] = wxs_acomp

        for user in wxs_users_list:
            try:
                user_status = checkStatus(user, wxs_visits_dict, wxs_acomp_dict)
                if user["CHState"] != user_status:
                    trace(f"User: {user['FirstName']} Status mudou")
                    user["CHState"] = user_status
                    updateUser(user)
                    createCard(user)
            
            except Exception as ex:
                report_exception(ex)
    except Exception as ex:
        report_exception(ex)

def main(conn):
    lock_cardholders_with_pendency(conn)
    reactivate_cardholders(conn)
    check_fornecedor()

debug = False
conn = False
if __name__ == '__main__':
    trace('Starting service: Integração Unimed Vale do Sinos - Versão 2.01')
    while True:
        if not conn:
            conn = sql_connect(conn)

        if debug:
            main(conn)
            sys.exit()
        else:
            main(conn)
            time.sleep(10)