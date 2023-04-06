# -*- coding: utf-8 -*-

import requests, sys, pyodbc
from requests.models import Response

# user_chid = str(sys.argv[1])
# user_chtype = int(sys.argv[2])
# user_companyid = str(sys.argv[3])
# user_partitionid = int(sys.argv[4])
user_chid = '2252'
user_chtype = 2
user_companyid = '5'
user_partitionid = 13

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

servername = 'NSP-USU-0098\W_ACCESS' # Servidor Marabras: W-ACCESS-SRV-HO\W_ACCESS 
userid = 'sa'
password = '#w_access_Adm#'
databasename = 'W_Access'
odbcdriver = '{ODBC driver 17 for SQL Server}'

def create_card(new_card, user_chid):
    #print(f'Creating new card.')
    create_card = requests.post(waccessapi_endpoint + f'cards', json=new_card)
    card = create_card.json()
    requests.post(waccessapi_endpoint + f'cardholders/{user_chid}/cards', json=card, headers=waccessapi_header, params=(("callAction", False),))
    #if card:
        #print(f'Cartão criado com CardID = {card["CardID"]}.') 
        #return(card)
    #else:
        #print(f'Erro ao criar cartão com ClearCode = {new_card["ClearCode"]}.')

def check_card(user_chid, companie_list):
    card_name = str(user_chid)
    card_name = f'F_{card_name.zfill(9)}' 
    new_card = { "ClearCode": card_name, "CardNumber": user_chid, "FacilityCode": 0, "CardType": 0, "PartitionID": companie_list["PartitionID"], "IsAutomaticCard": True }
    get_card = requests.get(waccessapi_endpoint + f'cards', params=(("limit", 1),("ClearCode", card_name)))
    get_card_json = get_card.json()
    if not get_card_json:
        card = create_card(new_card, user_chid)
    else:
        #print(f'Cartão {card_name} já existe')
        for card_object in get_card_json:
            teste = requests.post(waccessapi_endpoint + f'cardholders/{user_chid}/cards', json=card_object, headers=waccessapi_header, params=(("callAction", False),))
            teste = teste.json()
            print(teste)

if user_chtype == 2:
    # user = requests.get(waccessapi_endpoint + f'cardholders/' + str(user_chid), headers=waccessapi_header, params=(("CHType", user_chtype),("limit", '20000')))
    # user_list  = user.json()
    companie = requests.get(waccessapi_endpoint + f'companies/' + str(user_companyid), headers=waccessapi_header)
    companie_list = companie.json()
    card = check_card(user_chid, companie_list)
    if user_companyid in ('3', '4'):
        partitionid = 10
    else:    
        conn = pyodbc.connect('Driver='+odbcdriver+';Server='+servername+';UID='+userid+';PWD='+password+';Database='+databasename) 
        cursor = conn.cursor()
        nome_empresa = companie_list["CompanyName"]
        script_partition = f"select PartitionID from CfgSYPartitions where PartitionType = 1 and strLanguage2 like '%{nome_empresa}%'"
        cursor.execute(script_partition)
        for sql_row in cursor:
            partitionid = int(sql_row[0])
    if user_partitionid != partitionid:
        user = requests.get(waccessapi_endpoint + f'cardholders/' + str(user_chid), headers=waccessapi_header, params=(("CHType", user_chtype),("limit", '20000')))
        user_list  = user.json()       
        user_list["PartitionID"] = partitionid
        requests.put(waccessapi_endpoint + f'cardholders', json=user_list, headers=waccessapi_header, params=(("callAction", False),))
    else:
        sys.exit(0)
else:
    sys.exit(0)
