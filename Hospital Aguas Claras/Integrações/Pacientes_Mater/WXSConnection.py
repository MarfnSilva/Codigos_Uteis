# -*- coding: utf-8 # -*- 
from GenericTrace import *
import pyodbc, requests, inspect, json

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
    source_database_name = parser.get("config", "database")
    source_user_name = parser.get("config", "user")
    source_pwd_name = parser.get("config", "password")
    oracle_port = parser.get("config", "oraclePort")
    _dump_firts_iteration = parser.get("config", "DumpUsersInFirstIteration")
    dump_firts_iteration = True if _dump_firts_iteration == 'True' else False
    _interval_time = parser.get("config", "IntervalTime")
    interval_time = int(_interval_time)

    waccessapi_endpoint = f'http://{waccess_api_server}/W-AccessAPI/v1/'
    waccessapi_header = { 'WAccessAuthentication': f'{waccess_api_user}:{waccess_api_password}', 'WAccessUtcOffset': f'{waccess_utc_offset}' }
    

def sql_connect(conn):
    trace('Open Connection with database view', color='DarkViolet')
    trace('Establishing connection...', color='DarkViolet')
    conn = pyodbc.connect('Trusted_Connection=no;DRIVER={ODBC Driver 17 for SQL Server}; \
        SERVER='+WxsConn.source_server_name+'; \
        DATABASE='+WxsConn.source_database_name+'; \
        UID='+WxsConn.source_user_name+'; \
        PWD='+ WxsConn.source_pwd_name) # Produção
    if conn:
        trace('Connection successful.', color='Green')
    else:
        trace('Connect Error', color='salmon')
        conn = None
    return(conn)



def requests_get(method, params=None):
    try:
        reply = requests.get(WxsConn.waccessapi_endpoint + method, headers=WxsConn.waccessapi_header, params=params)
        if reply.status_code in [ requests.codes.ok , requests.codes.created ]:
            return(reply)
        elif reply.status_code == requests.codes.unauthorized:
            reply_json = json.loads(reply.text)
            trace(f'*** {reply_json["Message"]}')
            return(reply)
        elif reply.status_code == requests.codes.not_found:
            return(reply)
        else:
            trace(f'*** Unexpected response code: {reply.status_code} | {reply.reason}| \n{inspect.currentframe()}')
            return(reply)
    except Exception as ex:
        report_exception(ex)

def requests_post(method, params=None, json=None):
    try:
        parameters = params + (("callAction", False),) if params else (("callAction", False),)
        reply = requests.post(WxsConn.waccessapi_endpoint + method, headers=WxsConn.waccessapi_header, params=parameters, json=json)
        if reply.status_code in [ requests.codes.ok , requests.codes.created ]:
            return(reply)
        elif reply.status_code == requests.codes.unauthorized:
            reply_json = json.loads(reply.text)
            trace(f'*** {reply_json["Message"]}')
            return(reply)
        elif reply.status_code == requests.codes.not_found:
            return(reply)
        else:
            trace(f'*** Unexpected response code: {reply.status_code} | {reply.reason}| \n{inspect.currentframe()}')
            return(reply)
    except Exception as ex:
        report_exception(ex)

def requests_put(method, params=None, json=None):
    try:
        parameters = params + (("callAction", False),) if params else (("callAction", False),)
        reply = requests.put(WxsConn.waccessapi_endpoint + method, headers=WxsConn.waccessapi_header, params=parameters, json=json)
        if reply.status_code in [ requests.codes.ok, requests.codes.no_content ]:
            return(reply)
        elif reply.status_code == requests.codes.unauthorized:
            reply_json = json.loads(reply.text)
            trace(f'*** {reply_json["Message"]}')
            return(reply)
        elif reply.status_code == requests.codes.not_found:
            return(reply)
        else:
            trace(f'*** Unexpected response code: {reply.status_code} | {reply.reason}| \n{inspect.currentframe()}')
            return(reply)
    except Exception as ex:
        report_exception(ex)

def requests_delete(method, params=None, json=None):
    try:
        parameters = params + (("callAction", False),) if params else (("callAction", False),)
        reply = requests.delete(WxsConn.waccessapi_endpoint + method, headers=WxsConn.waccessapi_header, params=parameters, json=json)
        if reply.status_code in [ requests.codes.ok, requests.codes.no_content ]:
            return(reply)
        elif reply.status_code == requests.codes.unauthorized:
            reply_json = json.loads(reply.text)
            trace(f'*** {reply_json["Message"]}')
            return(reply)
        elif reply.status_code == requests.codes.not_found:
            return(reply)
        else:
            trace(f'*** Unexpected response code: {reply.status_code} | {reply.reason} | \n{inspect.currentframe()}')
            return(reply)
    except Exception as ex:
        report_exception(ex)

