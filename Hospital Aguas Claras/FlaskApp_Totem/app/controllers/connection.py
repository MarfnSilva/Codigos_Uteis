import requests, json, inspect, sqlite3
from app.controllers.GenericTrace import *

class WxsConn():
    import configparser
    a = 1
    parser = configparser.ConfigParser()
    # parser.read('D:\Projetos Python\Flask\Project 1\app\controllers\WXSIntegration.cfg')
    # waccess_api_server = parser.get("config", "WAccessAPIServer")
    # waccess_api_user = parser.get("config", "WAccessAPIUser")
    # waccess_api_password = parser.get("config", "WAccessAPIPassword")
    # waccess_utc_offset = parser.get("config", "WAccessUtcOffset")
    # source_server_name = parser.get("config", "serverName")
    # source_database_name = parser.get("config", "database")
    # source_user_name = parser.get("config", "user")
    # source_pwd_name = parser.get("config", "password")
    
    #waccessapi_endpoint = f'http://{waccess_api_server}/W-AccessAPI/v1/'
    #waccessapi_header = { 'WAccessAuthentication': f'{waccess_api_user}:{waccess_api_password}', 'WAccessUtcOffset': f'{waccess_utc_offset}' }
    
    waccessapi_endpoint = f'http://localhost/W-AccessAPI/v1/'
    waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180' }
    

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