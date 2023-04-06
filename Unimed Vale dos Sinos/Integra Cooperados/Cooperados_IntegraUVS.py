# -*- coding: utf-8 -*-

import cx_Oracle
import pyodbc, requests, json, traceback, sys
import datetime  
from datetime import *
from datetime import timedelta  
import base64
from Cooperados_WAccessApiClient import *
from GenericTrace import trace, report_exception
import time

import time
import servicemanager
import socket
import sys
import win32event
import win32service
import win32serviceutil
import os


def execute_one_iteration():
    try:
        trace("\n* Integração Cooperados Unimed Vale do Sinos: v1.05")

        # ---------------------------------- Dados servidor HOMOLOGAÇÃO ----------------------------------------
        #url = "http://w-accesshml.unimedvs.com.br/W-AccessAPI/v1/"

        # ---------------------------------- Dados servidor PRODUÇÃO ----------------------------------------
        url = "http://10.4.74.15/W-AccessAPI/v1/"
        h = { 'WAccessAuthentication': 'cooperados_integraUVS:#integra#', 'WAccessUtcOffset': '-180' }
        # ---------------------------------- Get all users in W-Access DB (Médicos) -----------------------------------

        trace("\n* Get all Cooperados - by IdNumber")

        reply = requests.get(url + 'cardholders', headers=h, params = (("CHType", '3'),("limit", '20000'), ("callAction", False)))
        if reply.status_code != requests.codes.ok:
            trace(f'HTTP reply error: {reply.url} {reply.status_code} - {reply.text}', color='salmon')
            return

        wxs_users_list = reply.json()
        # ---------------------------------- Get all Active Visits in W-Access -----------------------------------
        trace("\n* Get All Active Visits with CHType=7 (Pacientes)")

        reply = requests.get(url + 'cardholders/searchGeneric', headers=h, params = (("filter.cHType", '7'),("filter.startedVisits", True)))
        wxs_visits_list = reply.json()

        trace("\n* Get All Active Visits with CHType=1 (Visitantes/Acompanhantes)")

        reply = requests.get(url + 'cardholders/searchGeneric', headers=h, params = (("filter.cHType", '1'),("filter.startedVisits", True)))
        wxs_acomp_list = reply.json()

        #------------------------------------ Get all WXS ComboFields ----------------------------------------------------
        trace("\n* Get All Users ComboFields")

        reply = requests.get(url + 'chComboFields', headers=h, params = (("CHType", '3'),("limit", '20000')))
        wxs_comboFields_list = reply.json()

        #------------------------------------ Get all WXS Companies ----------------------------------------------------
        reply = requests.get(url + 'companies', headers=h, params = (("limit", '10000'),))
        wxs_companies_list = reply.json()

        # ----------------------------------- Reading RM View (Funcionários) -------------------------------------
        trace('\n** Reading MV View (Cooperados)')
        conn = cx_Oracle.connect('DBAMV/html5trn@172.22.0.197:1521/mv5trn') # Homologação
        #conn = cx_Oracle.connect('catrdb/uni_rdb@rac-cluster:1521/service_mv') # Produção

        cursor = conn.cursor()
        cursor.execute("SELECT COD_PRESTADOR, NOME_PRESTADOR, CPF, CRM, COD_VINCULO, SITUACAO, \
                        NOME_ESPECIALID FROM DBAMV.VDIC_UVS_CATRACA_PRESTADOR")


        wxs_users_dict = {}
        for wxs_user in wxs_users_list:
            if wxs_user["AuxText08"]:
                wxs_users_dict[wxs_user["AuxText08"].replace(".", "").replace("-","")] = wxs_user
            elif wxs_user["IdNumber"]:
                wxs_users_dict[wxs_user["IdNumber"].replace(".", "").replace("-","")] = wxs_user

        wxs_visits_dict = {} # -- Pacientes com internação ativa
        for wxs_visit in wxs_visits_list:
            if wxs_visit["IdNumber"]:
                wxs_visits_dict[wxs_visit["IdNumber"].replace(".", "").replace("-","")] = wxs_visit

        wxs_acomp_dict = {} # - Visitantes, acompanhantes e responsaveis
        for wxs_acomp in wxs_acomp_list:
            if wxs_acomp["IdNumber"]:
                wxs_acomp_dict[wxs_acomp["IdNumber"].replace(".", "").replace("-","")] = wxs_acomp

        n = 0 
        usu = 0
        sem = 0
        change = 0 
        for row in cursor:
            try:
                trace('------------------------------------------------------------------')
                trace(row)
                n+=1
                trace(f'Row count: {n}')
                #-------------------------------------- Set employees status ------------------------------------
                ativo = (row[5].upper() == "A")
                inativo = (row[5].upper() == "I")

                unimed_status = checkStatus(ativo, inativo, wxs_visits_dict, wxs_acomp_dict, row[2])
                
                #-------------------------------------- Set employees ComboFields ------------------------------------
                print(row[4], type(row[4]))
                if row[4] == 9:
                    vinculo = 'Cooperado'
                elif row[4] == 10:
                    vinculo = 'Unicoopmed'
                elif row[4] == 11:
                    vinculo = 'Prestador Terceiro'
                else:
                    vinculo = None

                unimed_fields = {
                    "AuxLst01": vinculo # Tipo de Vinculo
                }
                trace(unimed_fields)
                getComboFields(url, h, unimed_fields, wxs_comboFields_list)

                #-------------------------------------- Set employees Companies ------------------------------------

                #unimed_company = row[12]
                #unimed_company = getCompanies(url, h, unimed_company, wxs_companies_list)'
                #trace(f'CompanyID: {unimed_company}')
                
                # ---------------------------------- Read Unimed users - View -----------------------------------
                
                unimed_user = {
                    "FirstName": row[1], 
                    "AuxText08":str(row[0]), # Codigo Prestador
                    "IdNumber": row[2], # CPF
                    "AuxText10": row[6], # Especialidade
                    "AuxText01": row[3], # CRM
                    "AuxLst01": unimed_fields["AuxLst01"], # Tipo de Vinculo
                    "CHState": unimed_status,
                } 

                wxs_user = wxs_users_dict.get(unimed_user["AuxText08"]) ## AuxText08

                if wxs_user:
                    
                    usu += 1
                    fields_to_compare = [ "FirstName", "IdNumber", "AuxText10", "AuxText01", "AuxLst01", "CHState" ]
                    fields_with_difference = [ field for field in fields_to_compare if wxs_user[field] != unimed_user[field] ]
                    
                    # fields_with_difference = []
                    # for field in fields_to_compare:
                    #     if wxs_user[field] != unimed_user[field]:
                    #         fields_with_difference.append(field)


                    if fields_with_difference:
                        # user has changed
                        change += 1
                        trace(f'Usuário: {unimed_user["FirstName"]} Mudou. Campos com diferença: {fields_with_difference}')

                        for field in fields_with_difference:
                            trace(f'wxs_user: {wxs_user[field]}')
                            trace(f'unimed_user: {unimed_user[field]}')
                            wxs_user[field] = unimed_user[field]
                                
                        updateUser(url, h, wxs_user)
                        checkCard(url, h, wxs_user)
                        

                    else:
                        trace(f'Usuário: {unimed_user["FirstName"]}, com o CPF: {unimed_user["IdNumber"]} não sofreu nenhuma alteração.')

                        # -------------------------------- Tratar status dos usuários que não estão na view ---------------------------------

                    wxs_users_dict.pop(unimed_user["AuxText08"]) 

                else:
                    sem += 1
                    # Create user
                    trace(f'Nenhum usuário encontrado com o CPF {unimed_user["IdNumber"]}. Dados: {unimed_user}')
                    reply = createUser(url, h, unimed_user)
                    wxs_user = reply[1]
                    
                    #checkStatus(url, h, unimed_user, wxs_user)

            
            except Exception as ex:
                report_exception(ex)
                continue
                
           
        # ---- Tratamento dos Funcionários cadastrados no W-Access que estão com internação ou visitas ativas ---------

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
                ativaCartao(url, h, wxs_user)

            else:
                trace("Não altera CHState")


        trace(f'Total de usuários na view: {n}')
        trace(f'Usuário encontrados: {usu}')
        trace(f'Usuários não encontrados: {sem}')
        trace(f'Usuários alterados: {change}')

    except Exception as ex:
        report_exception(ex)


debug = False
if __name__ == '__main__':
    if debug:
        execute_one_iteration()
        sys.exit()

    while True:
            execute_one_iteration()
            time.sleep(20)
