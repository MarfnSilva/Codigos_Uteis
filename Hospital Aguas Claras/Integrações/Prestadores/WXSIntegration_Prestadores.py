# -*- coding: utf-8 # -*- 

from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests, json, traceback, sys, base64, re
from unidecode import unidecode
from WXSIntegrationClient import *
#from WXSIntegrationService import *
from GenericTrace import report_exception, trace
from WXSConnection import *

#def check_user(import_user_lst, all_access_levels):
def check_user(import_user_lst):
    # ---------------------------------- Read all users in W-Access ----------------
    try:
        #print(import_user_lst)
        trace(f'User with difference founded. Name = {import_user_lst["NOME"]} and ID = {import_user_lst["CPF"]}', color='RoyalBlue')
        global counter
        integration_key = 'IdNumber'

        cpf = import_user_lst["CPF"].replace(".", "").replace("-", "")
        # CHState = 2 > Demitido | CHState = 0  > Ativo
        chtype = set_chtype(import_user_lst["TIPO_PRESTADOR"])
        if import_user_lst["ATIVO"].upper() == 'ATIVO' or import_user_lst["ATIVO"].upper() == 'SIM':
            status = 0
        else:
            status = 1

        trace(f'Set (Status) in import user: received value = ({import_user_lst["ATIVO"]}) > wxs_user = index({status}) ', color='Goldenrod')
        import_user = {
            "FirstName" : import_user_lst["NOME"],
            "CHType" : chtype, # 5 - Prestador | 6 - Médico(a)
            "IdNumber" : cpf,
            "PartitionID" : 1, # Partição Padrão
            "CHState" : status,
            "AuxText05" : import_user_lst["TIPO_PRESTADOR"],
            "AuxText08" : import_user_lst["NR_CONSELHO"], # CRM
            "AuxText15" : str(import_user_lst["CD_PRESTADOR"]), # Código do Prestador
        }

        # ---------------------------------- Recebe os dados da View -----------------------------------
        trace(f'Get user with IdNumber = {import_user["IdNumber"]}')
        get_user = requests.get(WxsConn.waccessapi_endpoint + f'cardholders', headers=WxsConn.waccessapi_header, params=(("CHType", chtype),("IdNumber", import_user["IdNumber"])))
        get_user_json = get_user.json()
        print(get_user.status_code)

        if not get_user_json:
            cpf_get = '{}.{}.{}-{}'.format(import_user["IdNumber"][:3], import_user["IdNumber"][3:6], import_user["IdNumber"][6:9], import_user["IdNumber"][9:])
            get_user = requests.get(WxsConn.waccessapi_endpoint + f'cardholders', headers=WxsConn.waccessapi_header, params=(("CHType", chtype),("IdNumber", cpf_get)))
            get_user_json = get_user.json()
            print(get_user.status_code)
        
        if get_user_json:           
            for wxs_user in get_user_json:
                try:
                    trace(f'User found with chid = {wxs_user["CHID"]}')
                    counter["founded_in_waccess"] += 1
                    fields_to_compare = [ "FirstName", "AuxText05", "CHState", "AuxText08", "AuxText15" ]
                    fields_with_difference = [ field for field in fields_to_compare if wxs_user[field] != import_user[field] ]

                    if fields_with_difference:
                        counter["updated"] += 1
                        # user has changed
                        trace(f'Usuário: {import_user["FirstName"]} Mudou. Campos com diferença: {fields_with_difference}')
                        for field in fields_with_difference:
                            wxs_user[field] = import_user[field]

                        update_user(wxs_user)
                        #assign_access_level(wxs_user, all_access_levels)
                                        
                    else:
                        counter["no_changes"] += 1
                        trace(f'Usuário: {import_user["FirstName"]} não sofreu nenhuma alteração.')
                except Exception as ex:
                    report_exception(ex)     

        else:
            # Create user
            counter["new_user"] += 1
            trace('Usuário não encontrado')
            if import_user["CHState"] == 0:
                reply = createUser(import_user)
                reply_status_code = reply[0]
                wxs_user = reply[1]
                if reply_status_code == requests.codes.created:
                    trace(f'Cardholder Created : CHID = {wxs_user["CHID"]} - {wxs_user["FirstName"]}')
                    #assign_access_level(wxs_user, all_access_levels)
                    #assign_card(wxs_user)
                else:
                    trace('Erro na criação do usuário')
            else:
                trace('CHState is not Active. Passing create process.')
            
    except Exception as ex:
        report_exception(ex)

if __name__ == '__main__':
    firts_iteration = True
    current_set = set()
    trace("\n* Integração Prestadores - Hospital Aguas Claras : v1.00", color='gold')
        
    while True:
        counter = { "founded_in_waccess" : 0, "updated": 0, "new_user" : 0, "no_changes" : 0 , "total" : 0 }
        trace(f'Get all accesslevel in database')
        #all_access_levels = get_all_access_levels()

        url = "https://2n3gjx2wue-vpce-005982e4f40293b4f.execute-api.us-east-2.amazonaws.com/prod/v1/"
        proxies = {"http": "http://proxy.adhosp.com.br:8080"}

        credential = {"username": "invenzi", "password": "#407107Adm#"}
        headers = {
            'x-api-key': 'lAid2UFGAiarvPYY44IYr4caqKCVNNBx87HVxNin',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.put(url + 'authentication', headers=headers, json = credential)
            reply_json = response.json()
            id_token = reply_json['id_token']
            
            headers_2 = {
                'x-api-key': 'lAid2UFGAiarvPYY44IYr4caqKCVNNBx87HVxNin',
                'Content-Type': 'application/json',
                'Authorization' : id_token
            }
        except Exception as ex:
            report_exception(ex)

        try:
            reply = requests.get(url + f'prestadores', headers = headers_2)
            reply_json = reply.json()
        except Exception as ex:
            report_exception(ex)

        import_list = reply_json.get('Dados')
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(import_list, f, ensure_ascii=False, indent=4)
        new_set = set()
        user_changed = False

        if firts_iteration:
            trace(f'Dump cardholders in first iteration: [{WxsConn.dump_firts_iteration}]')

        for api_user in import_list:
            user_hash = hash(json.dumps(api_user))
            new_set.add(user_hash)
            if not user_hash in current_set:
                # trata a alteração/inserção do wxs_user
                trace('******** Check new api user')
                #check_user(api_user, all_access_levels)
                check_user(api_user)
                user_changed = True
                pass
        
        if not user_changed:
            trace('Nenhum usuário alterado nessa iteração')
        current_set = new_set
        time.sleep(WxsConn.interval_time)