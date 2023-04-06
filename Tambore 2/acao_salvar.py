# -*- coding: utf-8 # -*- 

from requests.models import Response
from datetime import *
from datetime import timedelta 
import requests, json, traceback, sys, base64, re
from GenericTrace import report_exception, trace
from WXSConnection import *
import pyodbc, requests, json, traceback, sys, csv
import os
from dateutil.relativedelta import relativedelta

#*************************************************Concatenação Rua************************************************ 


try:

    url = WxsConn.waccessapi_endpoint
    h = WxsConn.waccessapi_header


    servername = WxsConn.ccure_sql_servername
    userid = WxsConn.ccure_sql_userid
    password = WxsConn.ccure_sql_password
    databasename = WxsConn.ccure_sql_databasename

    conn = pyodbc.connect('Driver={ODBC driver 17 for SQL Server};Server='+servername+  ';UID='+userid+';PWD='+password+';Database='+databasename) 
    cursor = conn.cursor()

    set_chid = pyodbc.connect('Driver={ODBC driver 17 for SQL Server};Server='+servername+  ';UID='+userid+';PWD='+password+';Database='+databasename) 
    set_chid = set_chid.cursor()

    chid = int(sys.argv[1]) 
    chtype=int(sys.argv[2]) 
    comboIndex= sys.argv[3]
    check_auto=sys.argv[4]
    comboIndex_tipo= sys.argv[5]
    fieldID_unid = 'lstBDA_AuxLst02'


    trace(f'New user recieved: CHID={chid} | chtype={chtype} | comboIndex[AuxLst02]={comboIndex} | Accesso Academia[AuxChk02]={check_auto} | Tipo Morador[AuxLst03]={comboIndex_tipo}')

    # chid = '11018'
    # chtype= 2
    # comboIndex = '217' #Quadra/Lote
    # check_auto=1 #Acesso a Academia #
    # comboIndex_tipo='2' #Tipo Usuario#

    if chtype == 2:
        trace(f'User with CHType 2 : parametro recebido={chtype}')
        trace("\n* Get all Lista Rua - by index")
        reply = requests.get(url + 'chComboFields', headers=h, params = (("chtype",2),("fieldID",'lstBDA_AuxLst01')))
        wxs_rua_list = reply.json()

        trace("\n* Get Moradores - by IdNumber")
        # ---------------------------------- Get all users in W-Access DB -----------------------------------
        reply = requests.get(url + f'cardholders/{chid}', headers=h)
        wxs_users = reply.json()

        for r in wxs_rua_list:
            #print(r)
            if wxs_users["AuxLst01"] == r["ComboIndex"]:
                rua=r["strLanguage2"]
                
        #print(rua)

        wxs_users["AuxText13"]= f"{rua}, {wxs_users['AuxText04']}"

        reply = requests.put(url + 'cardholders', json=wxs_users,headers=h,params=(("callAction",False),)) 

        #*********************************************** Associação de Unidade ***********************************************

        trace("\n* Get all Lista Unidade - by index")
        reply = requests.get(url + 'chComboFields', headers=h, params = (("chtype",2),("fieldID", fieldID_unid), ("comboIndex", comboIndex)))
        wxs_unidade_list = reply.json()

        trace("\n* Get all Unidade - by index")
        reply = requests.get(url + 'cardholders', headers=h, params = (("chtype",3),))
        wxs_unidades = reply.json()

        #
        # print(wxs_unidades)

        for u in wxs_unidade_list:
            if wxs_users["AuxLst02"] == u["ComboIndex"]:
                unidade=u["strLanguage2"]

        print(unidade)

        if unidade == 'ADM':
            chid_unidade=323
        else:
            for un in wxs_unidades:
                if f"{unidade}" == un["FirstName"]:
                    chid_unidade=un["CHID"] 
            

        if unidade and chid_unidade:            
                linked_chid = {
                            "CHID": chid_unidade,
                            "LinkedCHID": chid,
                            "EscortsLinkedCH": False,
                            "EscortedByLinkedCH": False
                            }

                reply = requests.post(url + f'cardholders/{chid_unidade}/linkedCardholders', json=linked_chid,headers=h,params=(("callAction",False),)) 
                link = reply.json()
                #print(link)
                #print(unidade)
                #print(chid_unidade)

        #*********************************************** Associação de Grupos ***********************************************
        reply = requests.get(url + f'cardholders/{chid}',headers=h, params=(('includetables','Groups'),) )
        users_grup=reply.json()

        #print(users_grup)

        if users_grup["Groups"]:
            for gr in users_grup["Groups"]:
                groupid=gr["GroupID"]
                print(groupid)
                replay = requests.delete(url + f'cardholders/{chid}/groups/{groupid}',headers=h,params=(("callAction", False),))
                delete_g=reply.json()
                #print(delete_g)

        if comboIndex_tipo == '0' and check_auto:
            group_id=7
        elif comboIndex_tipo == '0' and not check_auto:
            group_id=2    
        elif comboIndex_tipo == '1' and check_auto:
            group_id=3
        elif comboIndex_tipo == '1' and not check_auto:
            group_id=8
        elif comboIndex_tipo == '2' and not check_auto:
            group_id=4
        elif comboIndex_tipo == '2' and check_auto:
            group_id=6
        else:
            group_id=None

        trace("\n* Grupo Associado - by IdNumber")

        print(comboIndex_tipo)
        print(group_id)
        
        reply = requests.post(url + f'cardholders/{chid}/groups/{group_id}', headers=h,params=(("callAction", False),)) 
        
        #*********************************************** Associação de Maior ***********************************************

        data_string=wxs_users["AuxDte02"]
        data_now=datetime.now()

        if data_string:
            data_string=data_string.replace('T', ' ')
            time_dte = datetime.strptime(data_string, '%Y-%m-%d %H:%M:%S').date()
            now = datetime.now()
            relative_date = relativedelta(now, time_dte)
            idade = relative_date.years

        
            if idade > 18:
                group_id=5
                print('Maior de idade')
                trace("\n* Grupo Associado - by IdNumber")
                reply = requests.post(url + f'cardholders/{chid}/groups/{group_id}', headers=h,params=(("callAction",False),)) 

            else:
                print('Menor')
        
        #********************************************* Associar Empresa ******************************************************
        reply = requests.get(url + f'cardholders/{chid}', headers=h)
        wxs_users_atualizar = reply.json()

        wxs_users_atualizar["CompanyID"]= 1

        reply= requests.put(url + f'cardholders/', headers=h,json=wxs_users_atualizar, params=(("callAction", False),))

        #***********************************************Criação do Ramal ****************************************************
        cursor.execute('select max (auxtext08) from chaux, chmain where chaux.chid=chmain.chid and chtype=2')
        for row in cursor:
            ultimo_ramal =  int(row[0])

        ramal_new = ultimo_ramal + 1

        print(ultimo_ramal)
        print(ramal_new)
        reply = requests.get(url + f'cardholders/{chid}', headers=h)
        wxs_users_atualizar = reply.json()

        if wxs_users_atualizar["AuxText08"]==None:

            wxs_users_atualizar["AuxText08"]= ramal_new
            reply= requests.put(url + f'cardholders/', headers=h,json=wxs_users_atualizar, params=(("callAction", False),))
            print(reply.content)
        else:
            print("Usuario com ramal")


        #*********************************************inserir ramal unidade no morador **************************************
        reply = requests.get(url + f'cardholders/{chid_unidade}', headers=h)
        wxs_unidade_morador = reply.json()

        ramal_unidade= wxs_unidade_morador["AuxText07"]
        print('Ramal unidade')
        print(ramal_unidade)

        reply = requests.get(url + f'cardholders/{chid}', headers=h)
        wxs_users= reply.json()

        wxs_users["AuxText07"] =ramal_unidade
        print(wxs_users)
        reply= requests.put(url + f'cardholders/', headers=h,json=wxs_users, params=(("callAction", False),))
        print(reply.content)

    #***********************************************Concatenar endereço e Ramal ******************************************* 
        reply = requests.get(url + f'cardholders/{chid}', headers=h)
        wxs_users= reply.json()

        wxs_users["AuxText12"]= f"Alameda: {wxs_users['AuxText13']} / Ramal:{wxs_users['AuxText07']}"

        reply = requests.put(url + 'cardholders', json=wxs_users,headers=h,params=(("callAction",False),)) 
    
    elif chtype == 4:

        #*********************************************** Criação Cartão Veiculo***********************************************

        reply = requests.get(url + f'cardholders/{chid}', headers=h, params=(("chtype",4),("fields",'CHID,FirstName,CHEndValidityDateTime')))
        wxs_users = reply.json()

        #print(wxs_users)

        placa= wxs_users["FirstName"]

        print(placa)
        #---------------------------------------------------Get Cartão --------------------------------------------------------------------------------------- 
        reply = requests.get(url +f'cards',headers=h, params=(("ClearCode",placa),))
        get_cartao=reply.json()

        #print(reply.status_code)

        if get_cartao:
            placa_2=placa
            print(placa_2)
        else:
            placa_2=''

        #---------------------------------------------------------------------------------------------------------------------------------------------------- 
    
        reply= requests.get(url+ f'cards/licensePlates/cardNumber?licensePlateText={placa}')
        card_placa = reply.json()
        print(card_placa)
        linked_card = {
                "ClearCode":placa,
                "CardNumber":card_placa,
                "FacilityCode": 0,
                "CardType": 0,
                "PartitionID": 0,
                "CardEndValidityDateTime": wxs_users["CHEndValidityDateTime"]}             
        print(linked_card)
        create_card = requests.post(url + 'cards', headers=h, json=linked_card , params = (("callAction", False),))
        create_card_json = create_card.json()
        create_card_json["CHID"] = wxs_users["CHID"]
        
        reply = requests.get(url +f'cards',headers=h, params=(("ClearCode",placa),))
        get_cartao=reply.json()
        print(get_cartao)

        for c in get_cartao:
            print(c)
            if placa == c["ClearCode"]:  
                print(c)
                assign_card = requests.post(url + f'cardholders/{chid}/cards',headers=h, json=c, params=(("callAction", False),))
                assign_card = assign_card.json()
                print(assign_card)

        sys.exit()

except Exception as ex:
    report_exception(ex)