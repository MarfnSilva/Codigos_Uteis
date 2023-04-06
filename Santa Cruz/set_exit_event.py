from GenericTrace import trace
import cx_Oracle, requests, json, sys
from dateutil import parser
from datetime import timedelta, datetime
from WXSConnection import *


def write_exit_time_new(user_name, user_chid, user_card, end_visit_str):
    date_dte = parser.parse(end_visit_str)
    date_dte = date_dte - timedelta(hours=3)
    date_str = date_dte.strftime("%d/%m/%Y %H:%M:%S")

    conn = False
    conn = data_source_connect(conn)

    cursor = conn.cursor()
    write_conn = conn.cursor()

    print(date_str)

    write_txt = f"update tasy.HBJ_CATRACA_ACESSO_hml \
                SET DT_SAIDA = TO_DATE('{date_str}','DD/MM/YYYY HH24:MI:SS'), \
                nm_usuario = 'Invenzi' where cd_pessoa_fisica = '{user_name}' and codigo='{user_card}'"

    trace(f'******** Escrevendo no Tasy (CHID={user_chid}): Nome={user_name}, codigo={user_card} | Hora da baixa:{date_str}')       
    #print(write_txt.strip())
    write_conn.execute(write_txt)
    # write_conn.commit()
    print()


user_chid = int(sys.argv[1]) # 64166 # Usuário Invenzi
user_name = sys.argv[2] #'invenzi'
#user_card = sys.argv[3] #44912
end_visit_dte = sys.argv[3] #datetime.now() 
user_chtype = int(sys.argv[4])

#end_visit_str = end_visit_dte.strftime("%Y-%m-%dT%H:%M:%S")

#trace(f'Teste -- CHID={user_chid}: Nome={user_name}')

if user_chtype == 1:
    get = requests_get(f'cardholders/{user_chid}', params=(("CHType", user_chtype),("includeTables", "LastVisit"), ("fields", "lastVisit")))
    get_json = get.json()
    user_card = get_json["LastVisit"]["ClearCode"]
    #end_visit_dte = get_json["LastVisit"]["VisitiEnd"]

    write_exit_time_new(user_name, user_chid, user_card, end_visit_dte)

else:
    sys.exit(0) 



