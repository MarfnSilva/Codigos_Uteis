# -*- coding: utf-8 # -*- 

from GenericTrace import report_exception, trace
import requests,pyodbc, json
from datetime import datetime, timedelta   
from Functions import *
import time
import openpyxl, pathlib, shutil


def script(arquivo, companie_list, accesslvl_list, end_validity_str):
    for arquivo in arquivos:
        print(arquivo)
        wb = openpyxl.load_workbook(filename =f'{arquivo}')
        import_list = wb.active
        for row in import_list.iter_rows(min_row=2, max_col=9, max_row=15000, values_only=True):
            a,b,c,d,e,f,g,h,i = row
            if h == None :
                trace(f'Usuário {a} não processado - Coluna EMPRESA, invalida!')
                continue
            # -------- Atribui PartitionID a partir do Nome da Empresa ------------
            for comp_id in companie_list:
                if str(comp_id["CompanyName"]).upper().strip() == str(h).upper().strip():
                    companyid = comp_id["CompanyID"]
                    partition_companyid = comp_id["PartitionID"]

            # -------- Atribui AccessLevelID a partir do Nome do Nível de Acesso ------------
            for access_id in accesslvl_list:
                if str(access_id["AccessLevelName"]).upper().strip() == str(c).upper().strip():
                    accesslvlid = access_id["AccessLevelID"] 

            # -------- Consulta no Banco para Atribuir o PartitionID do Usuário a partir do Nome da Empresa -----------
            if companyid in (3, 4):
                partitionid = 10
            else:    
                conn = pyodbc.connect('Driver='+odbcdriver+';Server='+servername+';UID='+userid+';PWD='+password+';Database='+databasename) 
                cursor = conn.cursor()
                script_partition = f"select PartitionID from CfgSYPartitions where PartitionType = 1 and strLanguage2 like '%{h}%'"
                cursor.execute(script_partition)
                for sql_row in cursor:
                    partitionid = sql_row[0]

            # --------- Montagem do Objeto ----------------
            if a != None:
                placa = str(d).replace("-", "").replace(" ", "").upper() if d != '' else None
                cpf = str(b).replace(".", "").replace("-", "").replace(" ", "") if b != '' else None
                chstate = 1 if i == 'DESATIVAR' else 0
                user = {
                    "FirstName" : str(a).upper().strip(),
                    "IdNumber" : cpf, 
                    "CHType" : 2, 
                    "CompanyID": companyid, 
                    "PartitionID" : partitionid, 
                    "CHState" : chstate, 
                    "CHEndValidityDateTime" : end_validity_str}
                print(user)

                # ---------- Finaliza o processo e exporta o motivo, caso não haja CPF no cadastro -----------
                if cpf == None or cpf == 'NONE':
                    trace(f'Erro ao Processar Usuário - Usuário sem CPF! ')
                    user["Motivo"] = (f'Usuário sem CPF! - {datetime.now()}')
                    with open('Not_Created.json', 'a', encoding='utf-8') as export:
                        json.dump(user, export, ensure_ascii=False, indent=4)
                        continue

                # -------- Atualiza o Usuário e Veículos ----------
                if i == 'ATUALIZAR':
                    trace(f'{i} - Usuário: {user["FirstName"]} CPF: {user["IdNumber"]}') 
                    user_get = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("CHType", user["CHType"]),("IdNumber", user["IdNumber"])))
                    user_get_json = user_get.json()
                    if user_get_json:
                        for wxs_user in user_get_json:
                            wxs_user["FirstName"] = user["FirstName"]
                            wxs_user["CompanyID"] = user["CompanyID"]
                            wxs_user["PartitionID"] = user["PartitionID"]
                            wxs_user["CHState"] = user["CHState"]
                            wxs_user["CHEndValidityDateTime"] = user["CHEndValidityDateTime"]
                            user_put = requests.put(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, json=wxs_user, params=(("callAction", False),))
                            card = check_card(wxs_user, partition_companyid)
                            assign_access_level(wxs_user, accesslvlid)
                            if placa != 'NONE':
                                    get_vehicle = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("nameSearch", placa),("CHType", 9),("includeTable", "Cards")))
                                    get_vehicle = get_vehicle.json()
                                    if get_vehicle:
                                        trace('Veiculo encontrado')
                                        for wxs_vehicle in get_vehicle:
                                            trace(f'Placa: {wxs_user["FirstName"]}')
                                            card_plate = generate_plate(placa)
                                            assign_card_plate(wxs_vehicle, card_plate, partition_companyid)
                                            assign_access_level(wxs_vehicle)
                                            associate_to_cardholder(wxs_user["CHID"], wxs_vehicle["CHID"])     
                                    else:
                                        trace('Veiculo não encontrado')
                                        new_car = { "FirstName": placa, "CHType": 4, "PartitionID": partitionid, "AuxText01": e, "AuxText02" : f, "AuxText03" : g, "CHEndValidityDateTime" : end_validity_str}
                                        reply = requests.post(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, json=new_car, params=(("callAction", False),))
                                        reply_json = reply.json()
                                        if reply.status_code == requests.codes.created:
                                            trace(f"Veículo Criado - CHID: {reply_json['CHID']}")
                                            wxs_vehicle = reply_json
                                            card_plate = generate_plate(placa)
                                            assign_card_plate(wxs_vehicle, card_plate, partition_companyid)
                                            assign_access_level(wxs_vehicle)
                                            associate_to_cardholder(wxs_user["CHID"], wxs_vehicle["CHID"])
                                        else:
                                            trace("Error: " + reply_json["Message"])
                                            print(reply_json)
                        trace(f'Usuário: {user["FirstName"]} CPF: {user["IdNumber"]} - Atualizado!')
                    else:
                        trace(f'Usuário: {user["FirstName"]} CPF: {user["IdNumber"]} não localizado, enviado para o fluxo de ADIÇÃO!')
                        i = 'ADICIONAR'

                # -------- Adiciona o Usuário e Veículos ----------    
                if i == 'ADICIONAR':
                    trace(f'{i} - Usuário: {user["FirstName"]} CPF: {user["IdNumber"]}') 
                    user_post = requests.post(waccessapi_endpoint + 'cardholders', json=user, headers=waccessapi_header, params=(("callAction", False),))
                    user_post_json = user_post.json()
                    if user_post.status_code == requests.codes.created:
                        #user_get = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("CHType", user["CHType"]),("nameSearch", user["FirstName"])))
                        user_get = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("CHType", user["CHType"]),("IdNumber", user["IdNumber"])))
                        user_get_json = user_get.json()
                        for wxs_user in user_get_json:
                            card = check_card(wxs_user, partition_companyid)
                            assign_access_level(wxs_user, accesslvlid)
                            if placa != 'NONE':
                                    get_vehicle = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("nameSearch", placa),("CHType", 9),("includeTable", "Cards")))
                                    get_vehicle = get_vehicle.json()
                                    if get_vehicle:
                                        trace('Veiculo encontrado')
                                        for wxs_vehicle in get_vehicle:
                                            print(f'Placa: {wxs_user["FirstName"]}')
                                            card_plate = generate_plate(placa)
                                            assign_card_plate(wxs_vehicle, card_plate, partition_companyid)
                                            assign_access_level(wxs_vehicle, accesslvlid)
                                            associate_to_cardholder(wxs_user["CHID"], wxs_vehicle["CHID"])     
                                    else:
                                        trace('Veiculo não encontrado')
                                        new_car = { "FirstName": placa, "CHType": 4, "PartitionID": partitionid, "AuxText01": e, "AuxText02" : f, "AuxText03" : g, "CHEndValidityDateTime" : end_validity_str}
                                        reply = requests.post(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, json=new_car, params=(("callAction", False),))
                                        reply_json = reply.json()
                                        if reply.status_code == requests.codes.created:
                                            trace(f"Veículo Criado - CHID: {reply_json['CHID']}")
                                            wxs_vehicle = reply_json
                                            card_plate = generate_plate(placa)
                                            assign_card_plate(wxs_vehicle, card_plate, partition_companyid)
                                            assign_access_level(wxs_vehicle, accesslvlid)
                                            associate_to_cardholder(wxs_user["CHID"], wxs_vehicle["CHID"])
                                        else:
                                            trace("Error ao criar veículo: " + reply_json["Message"])
                                            print(reply_json)
                        trace(f'Usuário: {user["FirstName"]} CPF: {user["IdNumber"]} - Adicionado!')
                    else:
                        trace(f'Erro ao {i} Usuário: {user["FirstName"]} CPF: {user["IdNumber"]} - Error: {user_post_json["Message"]}')
                        user["Motivo"] = (f'Erro ao {i} Usuário {user_post_json["Message"]} - {datetime.now()}')
                        with open('Not_Created.json', 'a', encoding='utf-8') as export:
                            json.dump(user, export, ensure_ascii=False, indent=4)
                            continue

                # -------- Desativa o Usuário e Veículos ----------
                if i == 'DESATIVAR':
                    trace(f'{i} - Usuário: {user["FirstName"]} CPF: {user["IdNumber"]}') 
                    user_get = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("CHType", user["CHType"]),("IdNumber", user["IdNumber"])))
                    user_get_json = user_get.json()
                    if user_get_json:
                        for wxs_user in user_get_json:
                            wxs_user["CHState"] = user["CHState"]
                            user_put = requests.put(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, json=wxs_user, params=(("callAction", False),))
                            if placa != None:
                                get_vehicle = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("nameSearch", placa),("CHType", 9),("includeTable", "Cards")))
                                get_vehicle = get_vehicle.json()
                                if get_vehicle:
                                    trace('Veiculo encontrado')
                                    for wxs_vehicle in get_vehicle:
                                        trace(f'Placa: {wxs_user["FirstName"]}')
                                        wxs_vehicle["CHState"] = user["CHState"]
                                        put_vehicle = requests.put(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, json=wxs_vehicle, params=(("callAction", False),))
                                        trace('Veiculo desativado')
                                else:
                                    trace('Veiculo não encontrado')
                                    continue
                        trace(f'Usuário: {user["FirstName"]} CPF: {user["IdNumber"]} - Desativado!')
                    else:
                        trace(f'Erro ao {i} Usuário: {user["FirstName"]} CPF: {user["IdNumber"]}')
                        user["Motivo"] = (f'Erro ao {i} Usuário {user_post_json["Message"]} - {datetime.now()}')
                        with open('Not_Created.json', 'a', encoding='utf-8') as export:
                            json.dump(user, export, ensure_ascii=False, indent=4)
                            continue
    
        
if __name__ == '__main__':

    accesslvl = requests.get(waccessapi_endpoint + f'accessLevels', headers=waccessapi_header)
    accesslvl_list = accesslvl.json()

    companie = requests.get(waccessapi_endpoint + f'companies', headers=waccessapi_header)
    companie_list = companie.json()

    while True:
        
        end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
        end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")

        date_file = datetime.now()
        date_file_str = date_file.strftime("%Y-%m-%d")

        trace('################## Inicio da Varredura #################', color = "gold")
        for file in companie_list:
            diretorio = pathlib.Path(f'{diretorio}')
            arquivos = tuple(diretorio.glob(f'**/{file["CompanyName"]}.xlsx'))
            if arquivos:
                for arquivo in arquivos:
                    trace(f'------- Arquivo encontrado com nome: {file["CompanyName"]}.xls -------', color = "blue")
                    script(arquivo, companie_list, accesslvl_list, end_validity_str)
                    shutil.move(f'{diretorio}/{file["CompanyName"]}.xlsx', f'{diretorio}/tratados/{file["CompanyName"]}_{date_file_str}.xlsx')
                    trace(f'------- Arquivo Processado -------', color = "blue")
            else:
                trace(f'------- Nenhum Arquivo Encontrado com o nome: {file["CompanyName"]}.xls -------', color = "gray")
                time.sleep(0.8)
        trace('#################### FIm da Varredura ##################', color = "gold")
        time.sleep(2) 