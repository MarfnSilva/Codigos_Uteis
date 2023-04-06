# -*- coding: utf-8 # -*- 

from datetime import timedelta
import requests, json, sys, time
#import cx_Oracle
from GenericTrace import report_exception, trace
from WXSConnection import *


if __name__ == '__main__':
    while True:
        try:
            external_zone_id = 3
            exit_readers = [
                    24, # ReaderName = 'L3 SAI CAT1 RCP CENT 1PAV'
                    25, # ReaderName = 'L4 SAI CAT1 RCP CENT 1PAV'
                    27, # ReaderName = 'SAI CAT PA GERAL TERREO'
                    31, # ReaderName = 'L PROX ENTRADA SERV1' | Catraca Bi-direcional
                    34, # ReaderName = 'L PROX ENTRADA SERV2' | Catraca Bi-direcional
                    93, # ReaderName = 'LEITORA CATRACA SADT' | Catraca Bi-direcional
                    90  # ReaderName = 'SAI PORTINHOLA SADT'
                    ]

            execute_query = f"SELECT codigo, cd_pessoa_fisica, cd_acesso, cd_tp_visitante, tp_visitante, dt_atualizacao, dt_saida, NM_USUARIO FROM tasy.HBJ_CATRACA_ACESSO_hml \
                                where DT_SAIDA is null and DT_ENTRADA > '2021-09-02 12:13:57' "

            conn = False
            conn = data_source_connect(conn)

            cursor = conn.cursor()
            write_conn = conn.cursor()

            cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'" " NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'")
            cursor.execute(execute_query)
            result = cursor.fetchall()

            count_user = {
                "total" : 0,
                "cond_1" : 0,
                "cond_2" : 0,
                "cond_3" : 0,
                "cond_4" : 0,
                "cond_5" : 0,
                "cond_6" : 0,
                "cond_7" : 0,
                "cond_8" : 0,
                "duplicado" : 0,
                "bypass" : 0
            }

            cond_2 = []
            cond_7 = []

            for codigo, cd_pessoa_fisica, cd_acesso, cd_tp_visitante, tp_visitante, dt_atualizacao, dt_saida, nm_usuario in result:
                #print(codigo, cd_pessoa_fisica, cd_acesso, cd_tp_visitante, tp_visitante, dt_atualizacao)
                #trace('----------- verificando novo usuário ----------')
                count_user["total"] += 1
                if cd_tp_visitante in [2,4,5,10,11,13,17,27,28,36,38]: # Visitantes | Tipo: Visitante
                    chtype = 1
                #elif cd_tp_visitante in [32, 35]: # Médicos | Tipo: Residente
                #    chtype = 7
                elif cd_tp_visitante in [3,7,9,12,19,20,22,26]: # Temporários | Tipo: Residente
                    chtype = 6
                elif cd_tp_visitante == 33: # Terceiros | Tipo: Residente
                    chtype = 5
                elif cd_tp_visitante in [34,37]: # Paciente - não tratar por enquanto
                    #trace(f' cd_tp_visitante: [{cd_tp_visitante}] Bypassing "Paciente"')
                    count_user["bypass"] += 1
                    continue
                else:
                    #trace(f'User {cd_pessoa_fisica} with cod_tp_visitante [{cd_tp_visitante}] not found')
                    continue

                reply = requests_get('cardholders', params=(("CHType", chtype), ("nameSearch", str(cd_pessoa_fisica)), ("includeTables", "ActiveVisit,LastVisit,LastTransit")))
                reply_json = reply.json() 
                i = 0 
                for user in reply_json:
                    if user["FirstName"] == cd_pessoa_fisica:
                        i += 1
                        if i > 1:
                            count_user["duplicado"] += 1

                        # ------------------- Visitantes --------------------
                        #----------------------------------------------------
                        if user["CHType"] == 1 and not user["ActiveVisit"] and user["LastVisit"]:
                            # Condição 1 : Usuário não possui visita ativa mas já realizou um acesso.
                            count_user["cond_1"] += 1
                            trace(f'>> Condição 1: Usuário {user["FirstName"]} com CHType = {chtype} encontrado - Usuário com visita encerrada.')
                            trace(f'Escrevendo data do encerramento da visita: {user["LastVisit"]["VisitEnd"]}', color='LightSeaGreen')
                            write_exit_time(user, user["LastVisit"]["VisitEnd"], codigo, write_conn)

                        elif user["CHType"] == 1 and user["ActiveVisit"]:
                            # Condição 2
                            count_user["cond_2"] += 1
                            cond_2.append(user["FirstName"])
                            #trace(f'>> Condição 2: Usuário {user["FirstName"]} | CHType = {chtype} ainda está com a visita ativa', color='YellowGreen')

                        # ------------------- Terceiros, Medicos e temporarios --------------------
                        #----------------------------------------------------            
                        elif user["CHType"] != 1 and user["CHState"] !=0:
                            trace(f'Usuário {user["FirstName"]} | CHType = {chtype} expirado, verificando leitora de saída')
                            if user["LastTransit"]:
                                # Condição 3
                                count_user["cond_3"] += 1
                                trace(f'>> Condição 3 | Usuário realizou ultimo transito na leitora: [{user["LastTransit"]["ReaderID"]}] {user["LastTransit"]["ReaderName"]} com o ZoneID: {user["LastTransit"]["ZoneID"]}')
                                if user["LastTransit"]["ReaderID"] in exit_readers and user["LastTransit"]["ZoneID"] == external_zone_id:
                                    # Condição 4
                                    count_user["cond_4"] += 1
                                    trace(f'>> Condição 4 | Enviando último acesso do usuário para o Tasy: {user["LastTransit"]["EventDateTime"]}', color='LightSeaGreen')
                                    write_exit_time(user, user["LastTransit"]["EventDateTime"], codigo, write_conn)
                                else:
                                    # Condição 5
                                    count_user["cond_5"] += 1
                                    trace(f'>> Condição 5 | Ultimo acesso do usuario não foi em uma das leitoras de saída, enviando o horario que o usuário expirou: {user["CHEndValidityDateTime"]}', color='Orange')
                                    write_exit_time(user, user["CHEndValidityDateTime"], codigo, write_conn)
                            else:
                                # Condição 6
                                count_user["cond_6"] += 1
                                trace(f'>> Condição 6 - Usuário não realizou nenhum acesso. LastTransit: {user["LastTransit"]}', color='Orange')
                                write_exit_time(user, user["CHEndValidityDateTime"], codigo, write_conn)

                        elif user["CHType"] != 1 and user["CHState"] == 0:
                            # Condição 7
                            cond_7.append(user["FirstName"])
                            #trace(f'>> Condição 7 - Usuário ainda está ativo: FirstName: {user["FirstName"]} | CHType: {user["CHType"]} | CHState : {user["CHState"]}')
                            count_user["cond_7"] += 1
                            

                        else:
                            # Condição 8
                            trace(f'>> Condição 8: FirstName: {user["FirstName"]} | CHType: {user["CHType"]} | LastTransit: Reader id {user["LastTransit"]}', color='red')
                            count_user["cond_8"] += 1

            trace(f'>> Condição 2 - Usuários que ainda estão com a visita ativa: {cond_2}', color='YellowGreen')                
            trace(f'>> Condição 7 - Usuários que ainda estão com a visita ativa: {cond_7}')
            trace(count_user, color='gold')
            time.sleep(WxsConn.interval_time)
       
        
        except Exception as ex:
            report_exception(ex)