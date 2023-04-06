# -*- coding: utf-8 -*-

import pyodbc, requests, json, sys, configparser
from GenericTrace import *
from libera_client import *


try:
    parser = configparser.ConfigParser()
    parser.read("libera_visita.cfg")
    url = "http://localhost/W-AccessAPI/v1/"
    h = { 'WAccessAuthentication': 'save_ch:#407107Adm#', 'WAccessUtcOffset': '-180' }

    # Visitor data
    wxs_chtype = int(sys.argv[1]) 
    wxs_visitor_type = sys.argv[2]
    wxs_temp_acomp = sys.argv[3]
    contact_chid = int(sys.argv[4])
    wxs_chid = sys.argv[5]

    # -------------------------------Testes --------------------------------
    #wxs_chtype = 1 # testes
    #wxs_visitor_type = '0'
    #wxs_temp_acomp = 'False'
    #contact_chid = 8763 # AGENDAMENTO CIRURGICO -- 5522.\
    #wxs_chid = 23078  --  107503

    user_partition = requests.get(url + f'cardholders/{wxs_chid}', headers=h)
    user_new_partition = user_partition.json()
    user_new_partition['PartitionID'] = 1
    requests.put(url + 'cardholders', headers=h, json = user_new_partition, params=(('callAction', False),))

    if contact_chid == 0:
        print('Usuário liberado sem contato de visita.')
        sys.exit(1)


    get_contact = requests.get(url + f'cardholders/{contact_chid}?includetables=chaccesslevels&fields=chid,auxchk06,auxtext08,auxtext09,auxlst04,partitionid,chtype,chaccesslevels', headers=h, params=())
    contact_user = get_contact.json()
    with open('teste.txt', 'w') as outfile:
        json.dump(contact_user, outfile)


    contact_sup_lib = contact_user["AuxChk06"]
    contact_max_vis = contact_user["AuxText08"]
    contact_max_acomp = contact_user["AuxText09"]
    contact_partition = contact_user["PartitionID"]
    contact_chtype = contact_user["CHType"]
    contact_accesslevels = contact_user["CHAccessLevels"]
    


    if contact_chtype == 9: # Add AccessLevels para Visitantes tipo Prestador!!
        for access_id in contact_user["CHAccessLevels"]:
            requests.post(url + f'cardholders/{wxs_chid}/accessLevels/{access_id["AccessLevelID"]}', json=access_id ,headers=h, params=(("callAction", False),))

    if wxs_chtype == 1 and wxs_visitor_type == '2': 
        for access_id in contact_user["CHAccessLevels"]:
            requests.post(url + f'cardholders/{wxs_chid}/accessLevels/{access_id["AccessLevelID"]}', json=access_id ,headers=h, params=(("callAction", False),))
    else:    
        if wxs_visitor_type == '0':
            if contact_partition in (2, 9):
                max_visits_by_contact = parser.get("config", "max_visit_adulto")
                max_visits_by_contact = int(max_visits_by_contact)
            if contact_partition in (4, 10):
                max_visits_by_contact = parser.get("config", "max_visit_pediatrico")
                max_visits_by_contact = int(max_visits_by_contact)

        elif wxs_visitor_type == '1':
            max_visits_by_contact = parser.get("config", "max_acomp")
            max_visits_by_contact = int(max_visits_by_contact)
        else:
            max_visits_by_contact = None


        # -------------------------------Testes --------------------------------

        if wxs_chtype != 1:
            print('\nUsuário não é visitante. Liberar visita')
            sys.exit(0)


        servername = parser.get("config", "SQLservername")
        userid = 'sa'
        password = '#w_access_Adm#'
        databasename = 'W_Access'

        if wxs_chtype == 1 and wxs_visitor_type == '2': # Visitor Type 2 = Prestador
            print('Visitante é um prestador')
            sys.exit(0)

        ## ---------------------------------- Check if user has more groups than AccessLevels ---------------------------
        conn = pyodbc.connect('Driver={ODBC driver 17 for SQL Server};Server='+servername+  ';UID='+userid+';PWD='+password+';Database='+databasename) 
        cursor = conn.cursor()
        script = f"With Main as ( \
                    Select \
                    (select count(CHID) from CHActiveVisits where ContactCHID = {contact_chid} and VisAuxLst01 = {wxs_visitor_type}) as Count_Contact \
                    ) \
                    select * from Main"

        cursor.execute(script)


        for row in cursor:
            active_vis_contact = row[0]
            if contact_sup_lib == True:
                if wxs_visitor_type == '0' and contact_max_vis:
                    max_visits_by_contact = int(contact_max_vis)
                
                elif wxs_visitor_type == '1' and contact_max_acomp:
                    max_visits_by_contact = int(contact_max_acomp)

            if active_vis_contact < max_visits_by_contact:
                assign_access_level(url, h, contact_user, wxs_chid)
                sys.exit(0)

            elif active_vis_contact == max_visits_by_contact:
                #print('\n - 6')
                if wxs_visitor_type == '0': # Visitor Type = 0 | Visitantes
                    #print('\n - 7')
                    print(f'\nO paciente já está com o limite de visitas permitidas.')
                    sys.exit(2)

                if wxs_visitor_type == '1':
                    #print('\n - 8')
                    if wxs_temp_acomp == 'True':
                        #print('\n - 9')
                        print('\nLiberação temporária autorizada.')
                        assign_access_level(url, h, contact_user, wxs_chid)
                        sys.exit(1)
                    
                    else:
                        #print('\n - 10')
                        print(f'\nO paciente já alcançou com o limite de acompanhantes permitidos.')
                        #print(f'\nQuantidade de visitas atual: {active_vis_contact} \nQnt Máxima de visitas permitidas: {max_visits_by_contact}')
                        sys.exit(2)

            else:
                #print('\n - 10')
                print(f'\nO paciente já alcançou com o limite de acompanhantes permitidos.')
                #print(f'\nQuantidade de visitas atual: {active_vis_contact} \nQnt Máxima de visitas permitidas: {max_visits_by_contact}')
                sys.exit(2)

            #print(f'\nQuantidade de visitas atual: {active_vis_contact} \nQnt Máxima de visitas permitidas: {max_visits_by_contact}')
            sys.exit(1)

except Exception as ex:
    report_exception(ex)
    sys.exit(1)