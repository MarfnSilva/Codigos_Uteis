from GenericTrace import trace
import cx_Oracle


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
    _dump_initial_iteration = parser.get("config", "Dump_Initial_Iteration") 
    dump_initial_iteration = True if _dump_initial_iteration == 'True' else False 
    
    waccessapi_endpoint = f'http://{waccess_api_server}/W-AccessAPI/v1/'
    waccessapi_header = { 'WAccessAuthentication': f'{waccess_api_user}:{waccess_api_password}', 'WAccessUtcOffset': f'{waccess_utc_offset}' }
    

def data_source_connect(conn):
    trace('Open Connection with Oracle view', color='DarkViolet')
    trace('Establishing connection...', color='DarkViolet')
    connection_string = f'{WxsConn.source_user_name}/{WxsConn.source_pwd_name}@{WxsConn.source_server_name}:{WxsConn.oracle_port}/{WxsConn.source_database_name}'
    conn = cx_Oracle.connect(connection_string) # Produção
    #print(conn.getinfo(WxsConn.source_server_name))
    if conn.version:
        trace('Connection successful.', color='Green')
        #writeTrace('', 'Connection successful.')
    else:
        trace('Connect Error', color='salmon')
        conn = None

    return(conn)