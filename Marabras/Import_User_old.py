# -*- coding: utf-8 # -*- 

from GenericTrace import report_exception, trace
import requests, json,csv#,base64
from datetime import datetime, timedelta   
from Functions import *
import time
import openpyxl

# waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
# waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}


try:
    wb = openpyxl.load_workbook(filename ='excel.xlsx')
    import_list = wb.active
    end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
    end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")
    for row in import_list.iter_rows(min_row=2, max_col=10, max_row=10000, values_only=True):
        a,b,c,d,e,f,g,h,i,j = row
        try:
            if a != None:
                placa = None#d.replace("-", "").replace(" ", "").upper() if d != '' else None
                cpf = b.replace(".", "").replace("-", "").replace(" ", "") if b != '' else None                        
                user = {
                    "FirstName" : a.upper().strip(),
                    "IdNumber" : cpf, 
                    "CHType" : int(i), 
                    "CompanyID": h, 
                    "PartitionID" : j, 
                    "CHState" : 0, 
                    "CHEndValidityDateTime" : end_validity_str}
                print(f'Importando {user["FirstName"]} - {user["IdNumber"]}') 
                user_post = requests.post(waccessapi_endpoint + 'cardholders', json=user, headers=waccessapi_header, params=(("callAction", False),))
                if cpf == None:
                    user_get = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("CHType", user["CHType"]),("nameSearch", user["FirstName"])))
                else:
                    user_get = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("CHType", user["CHType"]),("IdNumber", user["IdNumber"])))
                user_get_json = user_get.json() 
                if user_get_json:
                    for user_access in user_get_json:
                        companie = requests.get(waccessapi_endpoint + f'companies/' + str(user_access["CompanyID"]), headers=waccessapi_header)
                        companie_list = companie.json()
                        partition_car = int(companie_list["PartitionID"])
                        card = check_card(user_access, companie_list)
                        accesslevels = { "CHID" : user_access["CHID"], "AccessLevelID": int(c) , "AccessLevelStartValidity": None , "AccessLevelEndValidity": None}
                        assing = requests.post(waccessapi_endpoint + f'cardholders/{user_access["CHID"]}/accessLevels/{int(c)}', json=accesslevels, headers=waccessapi_header, params=(("callAction", False),))
                        if placa != None:
                            get_vehicle = requests.get(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, params=(("nameSearch", placa),("CHType", 9),("includeTable", "Cards")))
                            get_vehicle = get_vehicle.json()
                            if get_vehicle:
                                print('Carro encontrado')
                                for wxs_user in get_vehicle:
                                    print(f'Placa: {wxs_user["FirstName"]}')
                                    card_plate = generate_plate(placa)
                                    assign_card_plate(wxs_user, card_plate, companie_list)
                                    assign_access_level(wxs_user)
                                    associate_to_cardholder(user_access["CHID"], wxs_user["CHID"])     
                            else:
                                print('Carro não encontrado')
                                new_car = { "FirstName": placa, "CHType": 9, "PartitionID": j, "AuxText01": e, "AuxText02" : f, "AuxText03" : g, "CHEndValidityDateTime" : end_validity_str}
                                reply = requests.post(waccessapi_endpoint + 'cardholders', headers=waccessapi_header, json=new_car, params=(("callAction", False),))
                                reply_json = reply.json()
                                #print(reply_json)
                                if reply.status_code == requests.codes.created:
                                    print(f"Veículo Criado - CHID: {reply_json['CHID']}")
                                    wxs_user = reply_json
                                    card_plate = generate_plate(placa)
                                    assign_card_plate(wxs_user, card_plate, companie_list)
                                    assign_access_level(wxs_user)
                                    associate_to_cardholder(user_access["CHID"], wxs_user["CHID"])
                                else:
                                    print("Error: " + reply_json["Message"])
                                    print(reply_json)
                    print('Importação Realizada')                                        
                else:
                    print(f'Erro ao Criar Usuário - {user["FirstName"]} - {user["IdNumber"]}')
                    with open('Not_Created.json', 'a', encoding='utf-8') as export:
                        json.dump(user, export, ensure_ascii=False, indent=4)
        except Exception as ex_user:
            report_exception(ex_user)
        time.sleep(0.3) 
except Exception as ex:
        report_exception(ex)