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

def check_user(import_user_lst, all_access_levels):
    # ---------------------------------- Read all users in W-Access ----------------
    try:
        #print(import_user_lst)
        trace(f'User with difference founded. Name = {import_user_lst["nome"]} and ID = {import_user_lst["CPF"]}', color='RoyalBlue')
        global counter
        
        # --- Converter usuario para o padrão W-Access

        #cpf = import_user_lst["CPF"].replace(".", "").replace("-", "")

        # Set Unidade (AuxLst) and PartitionID
        if import_user_lst["unidade"] == 'HBR':
            unidade = 0
            partition = 6
        elif import_user_lst["unidade"] == 'MTN':
            unidade = 1
            partition = 7
        elif import_user_lst["unidade"] == 'HAC': 
            unidade = 2
            partition = 5
        elif import_user_lst["unidade"] == 'CADE':
            unidade = 3
            partition = 8
        else:
            None
            partition = 1

        trace(f'Set (Unidade) in import user: received value = ({import_user_lst["unidade"]}) > wxs_user = index({unidade}) ', color='Goldenrod')
        # CHState = 2 > Demitido | CHState = 0  > Ativo
        status = 2 if import_user_lst["status"].upper() == 'DEMITIDO' else 0
        trace(f'Set (Status) in import user: received value = ({import_user_lst["status"]}) > wxs_user = index({status}) ', color='Goldenrod')
        # Set Cardholder Partition
        
        cod_access_level = f'{import_user_lst["codigo_setor"]}_{import_user_lst["codigo_funcao"]}' if (import_user_lst["codigo_setor"] and import_user_lst["codigo_funcao"]) else None

        import_user = {
            "FirstName" : import_user_lst["nome"],
            "CHType" : 2, # Colaborador
            "IdNumber" : import_user_lst["CPF"],
            "PartitionID" : partition,
            "AuxLst02" : unidade,
            "AuxText04" : import_user_lst["DRT"],  # DRT
            "CHState" : status,
            "AuxText05" : import_user_lst["funcao"], # Cargo
            "AuxText06" : import_user_lst["setor"], # Setor
            "AuxText01" : cod_access_level, # Código do Nível de acesso 
            "AuxText09" : import_user_lst["gestor"]

        }
        # ---------------------------------- Recebe os dados da View -----------------------------------
        
        trace(f'Get user with IdNumber = {import_user["IdNumber"]}')
        get_user = requests.get(WxsConn.waccessapi_endpoint + f'cardholders', headers=WxsConn.waccessapi_header, params=(("CHType", 2),("IdNumber", import_user["IdNumber"])))
        wxs_user = get_user.json()
        print(get_user.status_code)

        if not wxs_user:
            cpf_get = import_user["IdNumber"].replace(".", "").replace("-", "")
            get_user = requests.get(WxsConn.waccessapi_endpoint + f'cardholders', headers=WxsConn.waccessapi_header, params=(("CHType", 2),("IdNumber", cpf_get)))
            wxs_user = get_user.json()
        
        if wxs_user:
            for user_dct in wxs_user:
                trace(f'User found with chid = {user_dct["CHID"]}')

                counter["founded_in_waccess"] += 1
                fields_to_compare = [ "FirstName", "AuxLst02", "CHState", "AuxText04", "AuxText05", "AuxText06", "AuxText01", "AuxText09", "PartitionID" ]
                fields_with_difference = [ field for field in fields_to_compare if user_dct[field] != import_user[field] ]

                if fields_with_difference:
                    counter["updated"] += 1
                    # user has changed
                    trace(f'Usuário: {import_user["FirstName"]} Mudou. Campos com diferença: {fields_with_difference}')
                    for field in fields_with_difference:
                        user_dct[field] = import_user[field]

                    update_user(user_dct)
                    assign_access_level(user_dct, all_access_levels)
                                    
                else:
                    counter["no_changes"] += 1
                    trace(f'Usuário: {import_user["FirstName"]} não sofreu nenhuma alteração.')

                
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
                    assign_access_level(wxs_user, all_access_levels)
                    #assign_card(wxs_user)

                else:
                    trace('Erro na criação do usuário')
            else:
                trace('CHState is not Active. Passing create process.')

    except Exception as ex:
        report_exception(ex)

firts_iteration = True
if __name__ == '__main__':
    
    current_set = set()
    trace("\n* Integração - Hospital Aguas Claras : v1.01", color='gold')
        
    while True:
        counter = { "founded_in_waccess" : 0, "updated": 0, "new_user" : 0, "no_changes" : 0 , "total" : 0 }
        trace(f'Get all accesslevel in database')
        all_access_levels = get_all_access_levels()

        url = "https://2n3gjx2wue-vpce-005982e4f40293b4f.execute-api.us-east-2.amazonaws.com/prod/v1/"
        proxies = {"http": "http://proxy.adhosp.com.br:8080"}

        credential = {"username": "invenzi", "password": "#407107Adm#"}
        headers = {
            'x-api-key': 'lAid2UFGAiarvPYY44IYr4caqKCVNNBx87HVxNin',
            'Content-Type': 'application/json'
        }

        response = requests.put(url + 'authentication', headers=headers, json = credential)
        reply_json = response.json()
        id_token = reply_json['id_token']
        
        headers_2 = {
            'x-api-key': 'lAid2UFGAiarvPYY44IYr4caqKCVNNBx87HVxNin',
            'Content-Type': 'application/json',
            'Authorization' : id_token
        }

        reply = requests.get(url + f'colaboradores', headers = headers_2, params=(("sistema", "SAP"),))
        reply_json = reply.json()
        with open('teste.txt', 'w', encoding='utf-8') as outfile:
            json.dump(reply_json, outfile)
        
        import_list = reply_json.get('Dados')
        user_changed = False
        new_set = set()

                    
        if firts_iteration and WxsConn.dump_firts_iteration:
            trace('Dump cardholders in first iteration.')
            firts_iteration = False
            for api_user in import_list:
                user_hash = hash(json.dumps(api_user))
                new_set.add(user_hash)

        else:
            firts_iteration = False
            for api_user in import_list:
                user_hash = hash(json.dumps(api_user))
                new_set.add(user_hash)
                if not user_hash in current_set:
                    # trata a alteração/inserção do wxs_user
                    trace('******** Check new api user')

                    check_user(api_user, all_access_levels)
                    user_changed = True
                    pass
            
            if not user_changed:
                trace('Nenhum usuário alterado nessa iteração')
        
        current_set = new_set
        time.sleep(WxsConn.interval_time)