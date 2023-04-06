from GenericTrace import trace
import cx_Oracle, requests, json
from dateutil import parser
from datetime import timedelta


class WxsConn():
    import configparser
    a = 1
    parser = configparser.ConfigParser()
    parser.read("WXSIntegration.cfg")
    gmtOffset = parser.get("config", "WAccessUtcOffset")
    gmtOffset = int(gmtOffset)
    waccess_api_server = parser.get("config", "WAccessAPIServer")
    waccess_api_user = parser.get("config", "WAccessAPIUser")
    waccess_api_password = parser.get("config", "WAccessAPIPassword")
    waccess_utc_offset = parser.get("config", "WAccessUtcOffset")
    source_server_name = parser.get("config", "serverName")
    source_database_name = parser.get("config", "serviceName")
    source_user_name = parser.get("config", "user")
    source_pwd_name = parser.get("config", "password")
    oracle_port = parser.get("config", "oraclePort")
    _interval_time = parser.get("config", "IntervalTime")  
    interval_time  = int(_interval_time)
    
    waccessapi_endpoint = f'http://{waccess_api_server}/W-AccessAPI/v1/'
    waccessapi_header = { 'WAccessAuthentication': f'{waccess_api_user}:{waccess_api_password}', 'WAccessUtcOffset': f'{waccess_utc_offset}' }
    

def data_source_connect(conn):
    trace('Open Connection with Oracle view', color='DarkViolet')
    trace('Establishing connection...', color='DarkViolet')
    connection_string = f'{WxsConn.source_user_name}/{WxsConn.source_pwd_name}@{WxsConn.source_server_name}:{WxsConn.oracle_port}/{WxsConn.source_database_name}'
    conn = cx_Oracle.connect(connection_string) # Produção
    #print(conn.getinfo(WxsConn.source_server_name))
    if conn.version:
        conn.autocommit = True
        trace('Connection successful.', color='Green')
        #writeTrace('', 'Connection successful.')
    else:
        trace('Connect Error', color='salmon')
        conn = None

    return(conn)

def requests_get(method, params=None):
    reply = requests.get(WxsConn.waccessapi_endpoint + method, headers=WxsConn.waccessapi_header, params=params)
    #print(reply.text, reply) 
    if reply.status_code in [ requests.codes.ok , 201 ]:
        return(reply)
    elif reply.status_code == requests.codes.unauthorized:
        reply_json = json.loads(reply.text)
        trace(reply_json["Message"])
        return(reply)
    elif reply.status_code == requests.codes.not_found:
        return(reply)


def write_exit_time(user, exit_time, codigo, write_conn):
    date_dte = parser.parse(exit_time)
    date_dte = date_dte - timedelta(hours=3)
    date_str = date_dte.strftime("%d/%m/%Y %H:%M:%S")

    write_txt = f"update tasy.HBJ_CATRACA_ACESSO_hml \
                SET DT_SAIDA = TO_DATE('{date_str}','DD/MM/YYYY HH24:MI:SS'), \
                nm_usuario = 'Invenzi' where cd_pessoa_fisica = '{user['FirstName']}' and codigo='{codigo}'"

    trace(f'******** Escrevendo no Tasy (CHID={user["CHID"]}): Nome={user["FirstName"]}, codigo={codigo} | Hora da baixa:{date_str}')       
    #print(write_txt.strip())
    write_conn.execute(write_txt)
    #print()