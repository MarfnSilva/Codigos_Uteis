# -*- coding: utf-8 -*-

import cx_Oracle
import pyodbc, requests, json, traceback, sys
import datetime  
from datetime import *
from datetime import timedelta  
import base64
from Funcionarios_WAccessApiClient import *
from GenericTrace import trace, report_exception
from WXSConnection import *
import time
import servicemanager
import socket
import sys
import win32event
import win32service
import win32serviceutil
import os


def execute_one_iteration(conn):
    write_txt('----------- nova iteração --------')
    try:
        integration_key = "AuxText10"
        # ---------------------------------- Dados servidor PRODUÇÃO ----------------------------------------
        url = "http://w-accesshml.unimedvs.com.br/W-AccessAPI/v1/"
        h = { 'WAccessAuthentication': 'funcionarios_integraUVS:#integra#', 'WAccessUtcOffset': '-180' }
        # ---------------------------------- Get all users in W-Access DB (Funcionários) -----------------------------------
        reply = requests_get('cardholders', params = (("CHType", '2'),("limit", '200000')))
        wxs_users_list = reply.json()
        print(len(wxs_users_list))
        # ---------------------------------- Get all Active Visits in W-Access -----------------------------------
        trace("Get All Active Visits with CHType=7 (Pacientes)")

        reply = requests_get('cardholders/searchGeneric', params = (("filter.cHType", '7'),("filter.startedVisits", True)))
        wxs_visits_list = reply.json()

        trace("Get All Active Visits with CHType=1 (Visitantes/Acompanhantes)")

        reply = requests_get('cardholders/searchGeneric', params = (("filter.cHType", '1'),("filter.startedVisits", True)))
        wxs_acomp_list = reply.json()
        
        #------------------------------------ Get all WXS ComboFields ----------------------------------------------------

        trace("Get All Users ComboFields")

        reply = requests_get('chComboFields', params = (("CHType", '2'),("limit", '20000')))
        wxs_comboFields_list = reply.json()

        #------------------------------------ Get all WXS Companies ----------------------------------------------------
        reply = requests_get('companies', params = (("limit", '1000'),))
        wxs_companies_list = reply.json()

        # ----------------------------------- Reading RM View (Funcionários) -------------------------------------
        trace('Reading RM View (Funcionários)')
        #conn = cx_Oracle.connect('catrdbrm/uni_rdbrm@uvs01-scan1.br1.ocm.s7067041.oraclecloudatcustomer.com:1521/service_rm.br1.ocm.s7067041.oraclecloudatcustomer.com') # Produção
        #trace(conn)
        cursor = conn.cursor()
        
        ## --- Comentar a linha abaixo caso o script seja executado no servidor de homologação.
        cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'" " NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'")
        ## ------------------------------------------------------------------------------------------

        cursor.execute("select nome, matricula, cpf, tipo, Filial, Area, secao,  \
                        funcao, admissao, demissao, ferias, afastamento, nomefilial, datademissao, id, \
                        inicioferias, fimferias, inicioafast, fimafast, datademissao, dataadmissao from rm.VW_UVS_CATRACA_ENTRADA \
                        where (datademissao > (select sysdate - INTERVAL '30' DAY from dual) \
                        or datademissao is null)")

        wxs_users_dict = {}
        for wxs_user in wxs_users_list:
            if wxs_user[integration_key]:
                    wxs_users_dict[wxs_user[integration_key].replace(".", "").replace("-","")] = wxs_user
            elif wxs_user["IdNumber"]:
                wxs_users_dict[wxs_user["IdNumber"].replace(".", "").replace("-","")] = wxs_user

            
        wxs_visits_dict = {}
        for wxs_visit in wxs_visits_list:
            if wxs_visit["IdNumber"]:
                wxs_visits_dict[wxs_visit["IdNumber"].replace(".", "").replace("-","")] = wxs_visit

        wxs_acomp_dict = {}
        for wxs_acomp in wxs_acomp_list:
            if wxs_acomp["IdNumber"]:
                wxs_acomp_dict[wxs_acomp["IdNumber"].replace(".", "").replace("-","")] = wxs_acomp

        n = 0
        usu = 0
        sem = 0
        change = 0
        state = 0

        for row in cursor:
            trace(f'Usuário: {row[0]}')
            if row[13]: 
                data_demissao_dte = row[13]
                data_demissao_str = data_demissao_dte.strftime("%Y-%m-%dT%H:%M:%S")
                trace(f'Data de Demissão: {data_demissao_str}')
                trace(f'Teste da data: {data_demissao_str}, tipo: {type(data_demissao_str)}')
                if data_demissao_dte < datetime.now() - timedelta(days=20):
                    trace(f'data anterior: Nâo tratar : {data_demissao_str}, tipo: {type(data_demissao_str)}')
                    continue
                    
                #elif data_demissao_dte > datetime.now() - timedelta(days=20):
                #    trace(f'data posterior: {data_demissao_str}, tipo: {type(data_demissao_str)}')   
            #else:
                #trace("Sem data de demissão")
            
            try:
               
                n += 1
                trace('------------------------------------------------------------------')
                trace(n)
                trace(row)

                #-------------------------------------- Set employees status ------------------------------------
                admissao = (row[8].upper() == "SIM")
                demissao = (row[9].upper() == "SIM")
                ferias = (row[10].upper() == "SIM")
                afastamento = (row[11].upper() == "SIM")
                # admissao_futura =  ## Considerar na integração
            
                unimed_status = checkStatus(admissao, demissao, ferias, afastamento, wxs_visits_dict, wxs_acomp_dict, row[2])
                
                #-------------------------------------- Set employees ComboFields ------------------------------------
                unimed_fields = {
                    "AuxLst01": row[5][:50].strip(), # Area   --  .strip()
                    "AuxLst02": row[6][:50].strip(), # Seção
                    "AuxLst03": row[7][:50].strip(), # Função
                    "AuxLst05": row[3][:50].strip()  # Tipo
                }
                trace(unimed_fields)
                getComboFields(url, h, unimed_fields, wxs_comboFields_list)

                #-------------------------------------- Set employees Companies ------------------------------------

                unimed_company = row[12][:50].strip()
                unimed_company = getCompanies(url, h, unimed_company, wxs_companies_list)
                trace(f'CompanyID: {unimed_company}')

                # ----------------------------------- Inicio/Fim das Ferias e Afastamento ------------
                if row[15]:
                    inicio_ferias = row[15].strftime("%Y-%m-%dT%H:%M:%S")
                else:
                    inicio_ferias = None
                if row[16]:
                    fim_ferias = row[16].strftime("%Y-%m-%dT%H:%M:%S")
                else:
                    fim_ferias = None
                if row[17]:
                    inicio_afast = row[17].strftime("%Y-%m-%dT%H:%M:%S")
                else:
                    inicio_afast = None
                if row[18]:
                    fim_afast = row[18].strftime("%Y-%m-%dT%H:%M:%S")
                else:
                    fim_afast = None
                if row[13]:
                    demissao = row[13].strftime("%Y-%m-%dT%H:%M:%S")
                else:
                    demissao = None
                if row[20]:
                    admissao_dte = row[20].strftime("%Y-%m-%dT%H:%M:%S")
                else:
                    admissao_dte = None                   
                # ---------------------------------- Read Unimed users - View -----------------------------------
                
                unimed_user = {
                    "FirstName": row[0], 
                    "AuxText15":row[1], # Matricula
                    "IdNumber": row[2], # CPF
                    "AuxText14": row[4], # Filial
                    "AuxLst01": unimed_fields["AuxLst01"], # Area
                    "AuxLst02": unimed_fields["AuxLst02"], # Secao
                    "AuxLst03": unimed_fields["AuxLst03"], # Funcao
                    "AuxLst05": unimed_fields["AuxLst05"],  # Tipo
                    "CHState": unimed_status,
                    "CompanyID": unimed_company,
                    "AuxText10" : str(row[14]), # ID do usuário dentro do Rm - Utilizado como chave única na integração.
                    "AuxDte04" : inicio_ferias, # Inicio das Ferias
                    "AuxDte05" : fim_ferias, # Fim das Ferias
                    "AuxDte06" : inicio_afast, # Inicio do Afastamento
                    "AuxDte07" : fim_afast, # Fim do Afastamento
                    "AuxDte08" : demissao, # Data de Demissão
                    "AuxDte09" : admissao_dte # Data de Admissão
                }

                #writeTrace(unimed_user["IdNumber"], f'Processing Unimed user: {unimed_user["FirstName"]}')
                trace(f'GET W_ACCESS USER: {unimed_user["IdNumber"]} tipo : {type(unimed_user["IdNumber"])}')
                wxs_user = wxs_users_dict.get(unimed_user[integration_key])

                if wxs_user:
                    usu += 1
                    if wxs_user["CHState"] == 0:
                        state += 1

                    fields_to_compare = [ "AuxText15", "FirstName", "AuxText14", "CHState", "AuxLst01", "AuxLst02", "AuxLst03", "AuxLst05", "CompanyID", "AuxText10", "AuxDte04", "AuxDte05", "AuxDte06", "AuxDte07", "AuxDte08", "AuxDte09"]
                    fields_with_difference = [ field for field in fields_to_compare if wxs_user[field] != unimed_user[field] ]

                    if fields_with_difference:
                        # user has changed
                        trace(f'Usuário: {unimed_user["FirstName"]} Mudou. Campos com diferença: {fields_with_difference}')
                        change += 1

                        for i in fields_with_difference:
                            trace(f'Unimed, campo {i}: {unimed_user[i]} : tipo: {type(unimed_user[i])}')
                            trace(f'W-Access, campo {i}: {wxs_user[i]} : tipo: {type(wxs_user[i])}')
                        
                        for field in fields_with_difference:
                            wxs_user[field] = unimed_user[field]

                        updateUser(url, h, wxs_user)
                        createCard(url, h, wxs_user)

                    else:
                        trace(f'Usuário: {unimed_user["FirstName"]}, com o CPF: {unimed_user["IdNumber"]} não sofreu nenhuma alteração.')

                    # -------------------------------- Tratar status dos usuários que não estão na view ---------------------------------
                    wxs_users_dict.pop(unimed_user[integration_key])
                    
                else:

                    sem += 1
                    # Create user
                    trace(f'Nenhum usuário encontrado com o CPF {unimed_user["IdNumber"]}')
                    createUser(url, h, unimed_user)
                    
            
            except Exception as ex:
                report_exception(ex)
                traceback.trace_exc(file=sys.stdout)
                conn = None


        # ---- Tratamento dos Funcionários cadastrados no W-Access que estão com internação ou visitas ativas ---------

        #trace(f'unimed_user: {i}')
        #trace(f'wxs_users_dict: {len(wxs_users_dict)}')
        #trace(f'wxs_visits_dict: {len(wxs_visits_dict)}')
        #trace(f'wxs_acomp_dict: {len(wxs_acomp_dict)}')
    
        for row in wxs_users_dict:
            wxs_user = wxs_users_dict[row]
            wxs_visit = wxs_visits_dict.get(row)
            wxs_acomp = wxs_acomp_dict.get(row)
            
            trace(wxs_user["FirstName"])
            if (wxs_acomp or wxs_visit) and wxs_user["CHState"] == 0:
                trace(f"Usuário {wxs_user['FirstName']} esta com um atendimento ativo no momento.")
                wxs_user["CHState"] = 9 
                updateUser(url, h, wxs_user)
            
            elif not (wxs_acomp or wxs_visit) and wxs_user["CHState"] == 9:
                trace(f"Usuário {wxs_user['FirstName']} normalizado, não esta mais com um atendimento ativo no momento.")
                wxs_user["CHState"] = 0 
                updateUser(url, h, wxs_user)
                createCard(url, h, wxs_user)

            else:
                trace("Não altera CHState")


        count_n = f'Quantidade total de funcionários na view: {n}'
        trace(count_n), write_txt(count_n)
        count_usu = f'Funcionários encontrados no W-Access: {usu}'
        trace(count_usu), write_txt(count_usu)
        count_sem = f'Funcionários que não estão no W-Access: {sem}'
        trace(count_sem), write_txt(count_sem)
        count_change = f'Usuários alterados: {change}'
        trace(count_change), write_txt(count_change)
        count_state = f'Usuários com CHState = 0 : {state}'
        trace(count_state), write_txt(count_state)

    except Exception as ex:
        report_exception(ex)
        time.sleep(20)
        conn = None

debug = False
if __name__ == '__main__':
    trace("Integração Funcionários unimed Vale do Sinos: v2.00", color='Gold')
    conn = None
    if debug:
        conn = data_source_connect(conn)
        execute_one_iteration(conn)
        sys.exit()

    while True:
        trace('------ Starting new iteration ----- ', color='Green')
        if not conn:
            conn = data_source_connect(conn)
        if conn:
            execute_one_iteration(conn)
            time.sleep(WxsConn.interval_time)

