# -*- coding: utf-8 -*-
from GenericTrace import trace
import cx_Oracle, requests, json, sys
from dateutil import parser
from datetime import timedelta, datetime


def write_exit_time(user_name, user_chid, user_card, end_visit_str):
    date_dte = parser.parse(end_visit_str)
    date_dte = date_dte - timedelta(hours=3)
    date_str = date_dte.strftime("%d/%m/%Y %H:%M:%S")

    print(date_str)
    

    # write_txt = f"update tasy.HBJ_CATRACA_ACESSO_hml \
    #             SET DT_SAIDA = TO_DATE('{date_str}','DD/MM/YYYY HH24:MI:SS'), \
    #             nm_usuario = 'Invenzi' where cd_pessoa_fisica = '{user['FirstName']}' and codigo='{codigo}'"

    # trace(f'******** Escrevendo no Tasy (CHID={user["CHID"]}): Nome={user["FirstName"]}, codigo={codigo} | Hora da baixa:{date_str}')       
    # #print(write_txt.strip())
    # write_conn.execute(write_txt)
    #print()


user_chid = 64166 # Usuário Invenzi
user_name = 'invenzi'
user_card = 44912

end_visit_dte = datetime.now() #+ timedelta(days=1825) # 1825 Days = 5 Years
end_visit_str = end_visit_dte.strftime("%Y-%m-%dT%H:%M:%S")
write_exit_time(user_name, user_chid, user_card, end_visit_str)
