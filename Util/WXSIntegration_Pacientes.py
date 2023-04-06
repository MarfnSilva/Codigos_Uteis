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

def check_user(import_user):
    # ---------------------------------- Read all users in W-Access ----------------
    try:
        
        global counter
        
        trace('** Check users with difference in Tasy view', color='RoyalBlue')

        # --- Converter usuario para o padrão W-Access
        import_user_lst = import_user

        integration_key = import_user_lst["prontuario"]
        trace(f'Working on user with medical record = {integration_key}', color='RoyalBlue')

        user_name = import_user_lst["nm_social_paciente"] if import_user_lst["utiliza_nome_social"].upper() == 'SIM' else import_user_lst["nm_paciente"]
        cpf = set_cpf_mask(import_user_lst["cpf"])
        vip = 0 if import_user_lst["vip"].upper() == 'SIM' else 1
        #idade = get_age(import_user_lst["dt_nascimento"]) if import_user_lst["dt_nascimento"] else None
        idade = import_user_lst["idade"]
        data_nasc = get_nasc(import_user_lst["dt_nascimento"])
        menor_idade = True if idade < 18 else False

        if menor_idade and not cpf:
            sem_cpf = True
            sem_doc = 1
        else:
            sem_cpf = False
            sem_doc = None

        # Set Partition: [Paciente] Adulto = 2 | [Paciente] Pediatrico = 4
        partition_id = 4 if (menor_idade and import_user_lst["cd_multi_empresa"] == 8) else 2  
        # Definir unidade de internação dos pacientes
        unid_internacao = get_unid_internacao(import_user_lst["unidade_internacao"]) if import_user_lst["tipo_atendimento"] == 'Internação' else None   
        leito = import_user_lst["ds_leito"] if import_user_lst["tipo_atendimento"] == 'Internação' else None   

        status = set_status(import_user_lst)

        import_user = {
            "FirstName" : user_name,
            "AuxText15" : str(integration_key), # Prontuario
            "CHType" : 8, # Pacientes
            "IdNumber" : cpf, # Prontuario
            "VisAuxText01" : import_user_lst["atendimento"], # Numero do Atendimento
            "AuxLst03" : vip, 
            "AuxDte01" : data_nasc,
            "AuxText07" : idade,
            "dt_nascimento" : idade,
            "AuxChk04" : sem_cpf,
            "AuxLst02" : sem_doc,
            "PartitionID" : partition_id,
            "AuxText05" : import_user_lst["nr_ramal"],
            "AuxText13" : leito,
            "AuxLst04" : unid_internacao,
            "AuxText11" : import_user_lst["nm_responsavel"],
            "AuxLst05" : status[0],
            "EndValidity" :  status[1],
            "dt_alta" : import_user_lst["dt_alta_hospitalar"]
        }

        trace(f'Get user with medical record = {import_user["AuxText15"]}')

        advanced_search = {"Main": {
                            "CHType" : 8,
                            "Item1": {
                            "SearchField": "CHAux.AuxText15",
                            "SearchCondition": "=",
                            "SearchValue": str(import_user["AuxText15"]),
                            "SearchText": ""
                        }}}

        get_user = requests.post(WxsConn.waccessapi_endpoint + f'cardholders/advancedSearch', headers=WxsConn.waccessapi_header, json=advanced_search, params=(("includeTables", "activeVisit, cards"),))
        wxs_user_list = get_user.json()

        if wxs_user_list:
            #wxs_user_list = get_user.json()
            for wxs_user in wxs_user_list:
                counter["founded_in_waccess"] += 1
                fields_to_compare = [ "FirstName", "IdNumber", "AuxLst03", "AuxText05", "AuxText13", "AuxLst04", "AuxText11", "AuxLst05", "AuxText07", "AuxChk04" ]
                fields_with_difference = [ field for field in fields_to_compare if wxs_user[field] != import_user[field] ]

                if fields_with_difference:
                    counter["updated"] += 1
                    # user has changed
                    trace(f'Usuário: {import_user["FirstName"]} Mudou. Campos com diferença: {fields_with_difference}')
                    for field in fields_with_difference:
                        wxs_user[field] = import_user[field]

                    update_user(wxs_user, import_user)
                                
                else:
                    counter["no_changes"] += 1
                    trace(f'Usuário: {import_user["FirstName"]} não sofreu nenhuma alteração.')
                    
                check_card(wxs_user)
                attendence = check_attendance(wxs_user, import_user)
                if attendence:
                    trace('Attendence OK')
                else:
                    new_attendence(wxs_user, import_user)
                continue
                    
        else:
            if not import_user["dt_alta"]:
                # Create user
                counter["new_user"] += 1
                trace(f'User {import_user["FirstName"]} not found in W-Access DB. Creating User')
                reply = create_user(import_user)
                reply_status_code = reply[0]
                wxs_user = reply[1]

                if reply_status_code == requests.codes.created:
                    trace(f'Cardholder Created : CHID = {wxs_user["CHID"]} - {wxs_user["FirstName"]}')
                    new_attendence(wxs_user, import_user)
                else:
                    trace('Erro na criação do usuário')
        
            else:
                trace(f'Usuário {import_user["FirstName"]} não foi encontrado no W-Access mas possui data de alta, usuário não será criado no W-Access.')

    except Exception as ex:
        report_exception(ex)

current_set = set()
counter = { "founded_in_waccess" : 0, "updated": 0, "new_user" : 0, "no_changes" : 0 , "total" : 0 }
if __name__ == '__main__':
    print('********* novo Iteração')
    while True:

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

        reply = requests.get(url + f'atendimento', headers = headers_2, params=(("dt_atendimento", '01/05/2021'),("cd_multi_empresa", '8')))
        reply_json = reply.json()
        #with open('export_file.json', 'r') as reader:
        #    file = json.load(reader)

        #with open('export_file.json', 'a', encoding="utf-8") as reader:
        #    reader.write(reply.text)

        #import_list = file.get('Dados')
        import_list = reply_json.get('Dados')
        
        new_set = set()
        for wxs_user in import_list:
            user_hash = hash(json.dumps(wxs_user))
            new_set.add(user_hash)
            if not user_hash in current_set:
                # trata a alteração/inserção do wxs_user
                check_user(wxs_user)
                pass
        current_set = new_set
        trace('------------------------ Fim da Integração ------------------------')
        trace(f'{counter}')
        time.sleep(5)