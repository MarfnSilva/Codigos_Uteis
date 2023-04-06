
import json, pyodbc, os.path
import datetime, time
from typing import Dict
from GenericTrace import *
import requests
from datetime import datetime, timedelta

global settings
settings = json.loads(open('settings.json').read())

def get_current_time_str():
    x = datetime.datetime.now()
    return "%04d/%02d/%02d %02d:%02d:%02d.%03d " % (x.year, x.month, x.day, x.hour, x.minute, x.second, x.microsecond // 1000)

def valid_plate_tolerance_seconds(event_date_time):
    now = datetime.utcnow()
    event_second = event_date_time.second
    event_date_time_str = event_date_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    now_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    difference = now - event_date_time
    difference = difference.seconds
    if difference < settings["valid_plate_tolerance_seconds"]:
        return 0
    elif difference > settings["total_plate_tolerance_seconds"]:
        return 1
    else:
        return 2

def load_settings():
    global settings
    settings = json.loads(open('settings.json').read())
    return settings

def default_url():
    global settings
    ip_server = settings["api_uri_hml"] if settings["is_homolog"] else settings["api_uri_prd"]
    return ip_server
    #"http://localhost/W-AccessAPI/v1/"


def default_corporate_url():
    global settings 
    corporate_ip_server = settings["corporate_prd_hml"] if settings["is_homolog"] else settings["corporate_prd_url"]
    return corporate_ip_server


def default_headers():
    global settings
    # h = {"WAccessAuthentication": "WAccessAPI:#WAccessAPI#", "WAccessUtcOffset": "-180"}
    h = {"WAccessAuthentication": f"{settings['api_user']}:{settings['api_password']}", "WAccessUtcOffset": "-180"}
    return h


def get_token():

    url = f'http://10.112.224.71:8888/SmartAPIHomologacao/api/token'

    payload=f'grant_type=password&username=vopak&password=7eb1b52ef062a2362df6197770ff6f85'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()

    return(f'Bearer {response_json["access_token"]}')
    

def token_corporate():
    if os.path.exists('Token.txt'):
        arr = os.listdir()
        for file in arr:
            foto_tmsp = os.path.getmtime('Token.txt')
            foto_dte = datetime.fromtimestamp(foto_tmsp)
            dt_object = datetime.fromtimestamp(time.time())

            if abs(dt_object - foto_dte).seconds >= 80000:
                trace(f'Apagar arquivo: {file}')
                os.remove('Token.txt')
                return(get_token())
            else:
                with open('Token.txt') as f:
                    contents = f.read()
                    return(contents)
    else:
        now = datetime.now()
        date_ = now.strftime("%d/%m/%Y")
        with open(f'Token.txt', 'w') as f:
            token = get_token()
            f.write(token)
            return(token)


def test_token():
    with open('Token.txt') as f:
        contents = f.read()
        return(contents)


def get(path, params=None, headers=default_headers(), expected_code=requests.codes.ok):
    #trace(f"GET {path}")
    reply = requests.get(f"{default_url()}{path}", headers=headers, params=params, verify=False)
    if expected_code:
        assert reply.status_code == expected_code
    return reply, reply.json()


def delete(path, params=None, headers=default_headers(), expected_code=requests.codes.no_content):
    trace(f"DELETE {path}")
    parameters = params + (("callAction", False),) if params else (("callAction", False),)
    reply = requests.delete(f"{default_url()}{path}", headers=headers, params=parameters, verify=False)
    if expected_code:
        assert reply.status_code == expected_code
    return reply


def post(path, json, params=None, headers=default_headers(), expected_code=requests.codes.created):
    trace(f"POST {path}")
    parameters = params + (("callAction", False),) if params else (("callAction", False),)
    reply = requests.post(f"{default_url()}{path}", headers=headers, json=json, verify=False, params=parameters)
    if expected_code:
        assert reply.status_code == expected_code
    return reply, reply.json()


def put(path, json, params=None, headers=default_headers(), expected_code=requests.codes.no_content):
    trace(f"PUT {path}")
    parameters = params + (("callAction", False),) if params else (("callAction", False),)
    reply = requests.put(f"{default_url()}{path}", headers=headers, params=parameters, json=json, verify=False)
    if expected_code:
        assert reply.status_code == expected_code
    return reply


def get_json_string(d):
    return json.dumps(d, indent=2, ensure_ascii=False)


def sql_connect(conn):
    trace('Open Connection with database view', color='DarkViolet')
    trace('Establishing connection...', color='DarkViolet')
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+ settings["sql_server"] +';DATABASE='+ settings["sql_database"] +';UID='+ settings["sql_user"] +';PWD='+ settings["sql_password"])
    if conn:
        trace('Connection successful.', color='Green')
    else:
        trace('Connect Error', color='salmon')
        conn = None
    return(conn)


def get_readers(reader_id):
    lpr_name_list = []
    for id in settings["lpr_readers"]:
        if id["reader_id"] == reader_id:
            for value in id["values"]:
                lpr_name_list.append(value["lpr_name"])
    
    return lpr_name_list


def registra_movimento_json(id_corporate, reader_name, event_date_time, idOcr, plate, lpr_url_image):
    reg_mov_json = settings["default_json_registra_movimento"]
    reg_mov_json["idCorporate"] = id_corporate
    reg_mov_json["pontoControle"] = reader_name
    dt_mov = event_date_time - timedelta(hours=3)
    dt_mov_str = dt_mov.strftime("%Y-%m-%d %H:%M:%S")
    reg_mov_json["dtMovimento"] = dt_mov_str
    tipo_mov = 'E' if 'E' in reader_name else 'S'
    reg_mov_json["tipoMov"] = tipo_mov
    reg_mov_json["idOcr"] = idOcr
    reg_mov_json["placaOcr"] = plate
    reg_mov_json["imagemOcr"] = lpr_url_image

    return reg_mov_json

def get_lpr_image(lpr_event_id):
    trace('Waiting ocr file')
    time.sleep(1)
    if os.path.isfile(f'C:\Program Files (x86)\W-Access Server\Web Application\OCR\EventID_{lpr_event_id}.PNG'):
        return(f'https://10.112.25.7/W-Access/OCR/EventID_{lpr_event_id}.PNG')
    else:
        trace('Imagem não encontranda')
        

def call_corporate(reg_mov_json):
    token = token_corporate()
    headers = {
    'FILIAL': 'VOPAK_ALEMOA_SMART',
    'Authorization': token,
    'Content-Type': 'application/json'
    }

    trace(f'Data sended = {reg_mov_json}')
    url_copr = default_corporate_url()
    response = requests.post(url_copr, headers=headers, json=reg_mov_json)

    if response.reason != 'OK':
       trace(f'/registraMovimento error: {response.text}', color = 'Salmon')
       trace('Refresing corporate token')
       os.remove('.\Token.txt')
    else:
        trace(response.text, color = 'MediumSeaGreen')

    return response


def set_event_property(event_id, value):
    event_property = {
            "Name": "Vopak_Area_6_Log",
            "Value": value
        }
    set_property = put(f'events/{event_id}/properties', json=event_property)
    trace(set_property.text)
