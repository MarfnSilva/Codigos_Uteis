# -*- coding: utf-8 -*-

import cx_Oracle
import pyodbc, requests, json, traceback, sys, time, os
import datetime  
from datetime import *
from datetime import timedelta  
import base64
from Pacientes_WAccessApiClient import *
import time
from GenericTrace import report_exception, trace
from WXSConnection import *

debug = False

def execute_one_iteration(conn, changed_ids):
    try:
        trace("[MV] Get Pacientes to process...", color='Chocolate')
        
        cursor_user = conn.cursor()
        if len(changed_ids) > 1000:
            start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
            script = f"SELECT cod_atend, cod_pac, foto, nm_paciente, NR_CPF, RG, DS_Leito, \
                            DT_ALTA, TIPO_ATEND, DS_UNID_INT, COD_EMPRESA, NM_EMPRESA, \
                            SN_MENOR_IDADE, PEND_FINAN, PEND_ALTA, DS_UNID_INT, ISOLAMENTO, LIB_VIS, JUST_LIB_VIS, ultima_atualiza_cad \
                            FROM DBAMV.VDIC_UVS_CATRACA_PACIENTES where dt_alta is null \
                            or dt_alta > '{start_date}'"
        else:
            script = f"SELECT cod_atend, cod_pac, foto, nm_paciente, NR_CPF, RG, DS_Leito, \
                DT_ALTA, TIPO_ATEND, DS_UNID_INT, COD_EMPRESA, NM_EMPRESA, \
                SN_MENOR_IDADE, PEND_FINAN, PEND_ALTA, DS_UNID_INT, ISOLAMENTO, LIB_VIS, JUST_LIB_VIS, ultima_atualiza_cad \
                FROM DBAMV.VDIC_UVS_CATRACA_PACIENTES where cod_pac in ({changed_ids})"    
        
        cursor_user.execute(script)
        trace("[MV] Get Pacientes to process... DONE", color='Chocolate')
        trace("Start to process users with difference...", color='Chocolate')

        count_users = { "i": 0, "total" : 0 }

        for row in cursor_user:
            try:
                # ---------------------------------- Recebe os dados da View -----------------------------------
                trace('------------------------------------------------------------------')
                count_users["i"] += 1
                trace(f'{count_users["i"]} : {row}')

                menor_idade = (row[12].upper() == "SIM") or (row[12].upper() == "S")
                unimed_pend_financ = (row[13].upper() != "N")
                unimed_pend_alta = (row[14].upper() == "SIM") or (row[14].upper() == "S")
                isolamento = (row[16].upper() == 'SIM') or (row[16].upper() == 'S') 
                lib_vis = (row[17].upper() == 'SIM') or (row[17].upper() == 'S') 

                last_modif_dte = row[19]
                last_modif_str = last_modif_dte.strftime("%Y-%m-%dT%H:%M:%S")
                #trace(f'Hora de alta: {last_modif_str}, tipo: {type(last_modif_str)}')  

                if row[7]:
                    data_alta = True
                    data_alta_dte = row[7] + timedelta(hours=7)
                    data_alta_str = data_alta_dte.strftime("%Y-%m-%dT%H:%M:%S")

                    if data_alta_dte > datetime.now():
                        endvalidity = data_alta_dte.strftime("%Y-%m-%dT%H:%M:%S")
                    else:
                        data_alta_dte = datetime.utcnow() + timedelta(hours=4)
                        endvalidity = data_alta_dte.strftime("%Y-%m-%dT%H:%M:%S")


                else:
                    data_alta = False
                    data_alta_dte = datetime.utcnow() + timedelta(days=100)
                    data_alta_str = None
                    endvalidity = data_alta_dte.strftime("%Y-%m-%dT%H:%M:%S")

                trace(f'Hora de alta: {data_alta_str}, tipo: {type(data_alta_str)}')  

                unimed_user = {
                    "VisAuxText01": str(row[0]), # CodAtendimento
                    "AuxText15": str(row[0]), # CodAtendimento
                    "AuxText05": str(row[1]), # Codigo do Paciente
                    "PhotoImport": row[2],
                    "FirstName": row[3],
                    "IdNumber": row[4], # CPF
                    #RGImport = row[5], # RG
                    "VisAuxTextA02": row[6], # Nome Leito
                    "AuxChk03": menor_idade, # Menor de idade 
                    "AuxChk10": unimed_pend_financ, # Pendencia
                    "AuxText09" : str(row[10]), # Código Unidade dos Atendimentos (Locais)
                    "AuxChk09" : unimed_pend_alta,
                    "VisAuxText02" : row[15], # Nome Unidade de Internação
                    "AuxDte10" : data_alta_str, # Data de alta do paciente
                    "VisAuxChk01" : isolamento,
                    "VisAuxChk02" : lib_vis, # visita liberada (Sim ou Não)
                    "VisAuxTextA01" : row[18], # Justifiativa da liberação da visita no MV
                    "AuxText11" : last_modif_str, # Identifica se a foto do usuário precisa ser atualizada
                    "CHEndValidityDateTime" : endvalidity
                }

                criteria = {"Main": {
                        "CHType" : 7,
                        "Item1": {
                        "SearchField": "CHAux.AuxText05",
                        "SearchCondition": "=",
                        "SearchValue": unimed_user["AuxText05"],
                        "SearchText": "" }}}

                getuser = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/advancedSearch', json=criteria, headers=WxsConn.waccessapi_header, params=(("includeTables", "ActiveVisit"),) )
                getuser_json = getuser.json()

                if getuser_json:
                    for wxs_user in getuser_json:
                        #wxs_user = wxs_users_dict.get(unimed_user["AuxText05"])
                        if wxs_user:
                            fields_to_compare = [ "IdNumber", "FirstName", "AuxChk10", "AuxChk03", "AuxChk09",  "AuxDte10", "AuxText11", "AuxText09"]
                            fields_with_difference = [ field for field in fields_to_compare if wxs_user[field] != unimed_user[field] ]
                            
                            #if "AuxDte10" in fields_to_compare:

                            if fields_with_difference:

                                # user has changed
                                trace(f'Usuário: {unimed_user["FirstName"]} Mudou. Campos com diferença: {fields_with_difference}')
                                for field in fields_with_difference:
                                    wxs_user[field] = unimed_user[field]

                                updateUser(wxs_user, unimed_user)

                            else:
                                trace(f'Usuário: {unimed_user["FirstName"]} não sofreu nenhuma alteração.')
                            
                            # --------- Check if visit is started -----
                            checkVisit(wxs_user, unimed_user)
                        continue
                else:
                    # Create user
                    trace('Usuário não encontrado')
                    reply = createUser(unimed_user)
                    reply_status_code = reply[0]
                    cardholder = reply[1]

                    if reply_status_code == requests.codes.created:
                        # ---------- Check if "Data da Alta" is expired ------
                        if data_alta_dte > datetime.now(): 
                            trace(f'Data unimed: {data_alta_dte} e data atual: {datetime.now()}')
                            trace('Data alta Maior')
                            newVisit(cardholder, unimed_user) 

                        elif data_alta_dte < datetime.now(): # Se data de alta menor que a data atual a visita não será iniciada
                            trace('Data alta Menor')
                    else:
                        trace('Erro na criação do usuário')

            except Exception as ex:
                report_exception(ex)

    except Exception as ex:
        report_exception(ex)

current_set = set()
if __name__ == '__main__':
    first_iteration = True
    trace("Integração Pacientes unimed Vale do Sinos: v2.01", color='Gold')
    conn = None
    if debug:
        conn = data_source_connect(conn)
        trace("Getting users with difference", color='DeepSkyBlue')
        changed_ids,changed_users,new_set = users_with_difference(conn, current_set)
        if not changed_users:
            trace("No users with a difference were found in the database", color='DeepSkyBlue')
        else:
            trace(f"Users with difference: {len(changed_users)}", color='SteelBlue')
            trace(f"UsersIDs with difference: {changed_ids}", color='SteelBlue')
            execute_one_iteration(conn, changed_ids)
        sys.exit()

    while True:
        trace('------ Starting new iteration ----- ', color='Green')
        if not conn:
            conn = data_source_connect(conn)
        if conn:
            changed_ids,changed_users,new_set = users_with_difference(conn, current_set, first_iteration)
            first_iteration = False
            if not changed_users:
                trace("No users with a difference were found in the database", color='DeepSkyBlue')
            else:
                trace(f"Users with difference: {len(changed_users)}", color='SteelBlue')
                trace(f"UsersIDs with difference: {changed_ids}", color='SteelBlue')
                execute_one_iteration(conn, changed_ids)
        current_set = new_set
        time.sleep(2/10)