# -*- coding: utf-8 # -*- 

from GenericTrace import report_exception, trace
import requests, json,csv#,base64
from datetime import datetime, timedelta   
import time
import openpyxl


with open('teste_02.csv', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter= ',')
        csv_reader.__next__()
        end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
        end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")
        for row in csv_reader:
                placa = []#row[3].replace('-', '') if row[3] != '' else None
                cpf = row[1].replace(".", "").replace("-", "").replace(" ", "") if row[1] != '' else None                        
                user = {
                "FirstName" : row[0].upper().strip(),
                 "IdNumber" : cpf, 
                 "CHType" : int(row[8]), 
                 "CompanyID": row[7], 
                 "PartitionID" : row[9], 
                 "CHState" : 0, 
                 "CHEndValidityDateTime" : end_validity_str
                 }
                user["Motivo"] = (f'Cadastro Sem CPF! - {datetime.now()}')
                print("teste de texto = %s"%(user["FirstName"]))
                # print(user) 
                # print(f'Importando {user["FirstName"]} - {user["IdNumber"]}') 