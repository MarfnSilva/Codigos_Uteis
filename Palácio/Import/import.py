# -*- coding: utf-8 # -*- 

from GenericTrace import report_exception, trace
import requests, json,csv#,base64
from datetime import datetime, timedelta   
import time
import pyodbc

url = "http://localhost/W-AccessAPI/v1/"
h = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180' }

def get_combo_index(text, fieldID):
    conn2 = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\W_ACCESS;DATABASE=W_Access;UID=sa;PWD=#w_access_Adm#') # Produção
    with conn2.cursor() as get_combo:
        script = f"""
                SELECT ComboIndex, strLanguage2 from W_Access..CfgCHComboFields
                where FieldID = '{fieldID}'
                and strLanguage2 = '{text}'
                """
        #print(script)
        get_combo.execute(script)
        for comboIndex, language in get_combo.fetchall():
            return comboIndex

def create_card(cardnumber, cardholder):
    print('Criando Cartão')
    try:
        new_card = {"ClearCode": f'{cardnumber}', "CardNumber" : cardnumber, "FacilityCode": 0, "CardType": 0, "PartitionID": 0,}
        create_card = requests.post(url + 'cards', headers=h, json=new_card)
        create_card_json = create_card.json()
        assign_card = requests.post(url + f'cardholders/{cardholder["CHID"]}/cards', headers=h, json=create_card_json)
        print(f'Cartão associado: {assign_card.reason}')
    except Exception as ex:
        report_exception(ex)  


with open('import_novo.csv', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter= ',')
        # csv_reader.__next__()
        end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
        end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")
        for row in csv_reader:
                unidade = get_combo_index(row[5], 'lstBDA_AuxLst01')
                # placa = []#row[3].replace('-', '') if row[3] != '' else None
                # cpf = row[1].replace(".", "").replace("-", "").replace(" ", "") if row[1] != '' else None                        
                user = {
                "FirstName" : row[1].upper().strip(),
                 "IdNumber" : row[6], 
                 "CHType" : 2,
                 "AuxLst01" : unidade,
                 "AuxText02" : row[9],
                 "Cardnumber" : row[2], 
                 "PartitionID" : 1, 
                 "CHState" : 0, 
                 "CHEndValidityDateTime" : end_validity_str
                 }
                
                reply = requests.post(url + 'cardholders', headers=h, json=user)
                reply_json = reply.json()
                if reply.status_code == requests.codes.created:
                        print("New CHID: %d"%(reply_json["CHID"]))
                        create_card(user["Cardnumber"], reply_json)
                print(user)