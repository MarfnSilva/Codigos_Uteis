# -*- coding: utf-8 -*-

import json, sys, requests
from requests import status_codes
from tenacity import retry
from GenericTrace import *
from datetime import datetime, timedelta
from requests.exceptions import Timeout
from math import remainder

global settings
settings = json.loads(open('settings.json').read())


def check_full_db_verify(full_db_verify):
    import datetime
    now = datetime.datetime.now()
    if full_db_verify and now.minute == 11:
        return(False)
    elif now.minute == 12:
        return(True)
    

def read_last_iteration():
    # ------------------ Read last iteration datetime -----------
    trace('Reading last iteration datetime file')
    f = os.path.isfile('last_modify.txt')
    if f:
        with open('last_modify.txt', 'r') as last_modify:
            last_modify = last_modify.read()
        trace(f'Last iteration file founded. Value: {last_modify}')
        datetime_now = (datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_modify = (datetime.now() - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
        trace(f'File not found. Setting initial date = {last_modify}')
        datetime_now = (datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")
    
    return(last_modify, datetime_now)


def write_iteration_datetime(datetime_now):
    last_modify = datetime_now
    trace(f'Writing last iteration date: {last_modify}')
    with open('last_modify.txt', 'w') as f:
        f.write(last_modify)    
        trace(f'Write last iteration date: OK')  


def iam_alive_log(log):
    now = datetime.now()
    if remainder(now.minute,5) == 0 and log:
        trace('Meerkat Integration: still runing')
        return(False)
    elif remainder(now.minute,5) == 1:
        return(True)
    else:
        return(False)


def update_meerkat_users(cardholders_to_update):
    for ip in settings["meerket_ip_servers"]:
        try:
            meerkat_ip_server = ip["meerkat_server_ip"]
            print(f'Working with server: {meerkat_ip_server}')
            app_key = ip["appKey"]
            if not app_key:
                continue

            for user in cardholders_to_update:
                try:
                    delete_enrolled_user(user["label"], app_key, meerkat_ip_server)
                    print(f'Sending {user["label"]}')
                    enroll_user = requests.post(f'{meerkat_ip_server}/faces', headers={'content-type': 'application/json'}, json=user, timeout=3)
                    if enroll_user.status_code != 200:
                        print('Error')
                    print(f'Face {user["label"]}: OK')
                except Exception as ex:
                    report_exception(ex)
                    write_txt(ex)

        except Exception as ex:
            report_exception(ex)
            write_txt(ex)    


def delete_enrolled_user(user, app_key, meerkat_ip_server):
    print(f'Deleting {user}')
    del_headers = {
        'content-type': "application/json",
        'app_key': app_key
        }

    del_face = requests.delete(f'{meerkat_ip_server}/people/{user}', headers=del_headers)
    if del_face.status_code == 204:
        print(f'Delete Face {user}: OK')


def delete_cardholder_all_meekat_servers(user):
    for ip in settings["meerket_ip_servers"]:
        meerkat_ip_server = ip["meerkat_server_ip"]
        print(f'Working with server: {meerkat_ip_server}')
        app_key = ip["appKey"]
        if not app_key:
            continue

        delete_enrolled_user(f'CHID_{user}', app_key, meerkat_ip_server)


def get_wxs_users(last_modify):
    try:
        get_user = requests_get('cardholders', params=(("CHType", 2),("CHType", 3),("CHType", 7),("CHType", 8),("lastModifDateTimeStart", last_modify),
                                                        ("fields", "CHID,Firstname,CHType,CHState,Cards"),("includeTables", "Cards")))
        get_user_json = get_user.json()
        cardholders_to_update = []
        for cardholder in get_user_json:
            try:
                if cardholder["CHType"] not in settings["face_multi_factor_ch_types"]:
                    trace(f'Bypass - usuário [{cardholder["FirstName"]}] sem dupla autenticação')
                    continue
            
                wxs_photo = requests_get(f'cardholders/{cardholder["CHID"]}/photos/1')
                wxs_photo = wxs_photo.json()
                if not wxs_photo or not cardholder["Cards"] or cardholder["CHState"]:
                    wxs_photo = wxs_photo[:15] if wxs_photo else None
                    cards = True if cardholder["Cards"] else None
                    print(f"Bypass user: Photo= '{wxs_photo}...' | Card= {cards} | CHState= {cardholder['CHState']}")
                    delete_cardholder_all_meekat_servers(cardholder["CHID"])
                    continue

                trace(f'Send user CHID={cardholder["CHID"]} | {cardholder["FirstName"]}')
                meerkat_body = {
                    "label": f'CHID_{cardholder["CHID"]}',
                    "imageB64" : wxs_photo
                }
                cardholders_to_update.append(meerkat_body)

            except Exception as ex:
                report_exception(ex)
                write_txt(ex)
                
        return(cardholders_to_update)

    except Exception as ex:
        report_exception(ex)
        write_txt(ex)


def default_url():
    global settings
    return settings["api_uri"]
    #"http://localhost/W-AccessAPI/v1/"


def default_headers():
    global settings
    h = {"WAccessAuthentication": "WAccessAPI:#WAccessAPI#", "WAccessUtcOffset": "-180"}
    h = {"WAccessAuthentication": f"{settings['api_user']}:{settings['api_password']}", "WAccessUtcOffset": "-180"}
    return h


def requests_get(path, params=None, headers=default_headers(), expected_code=requests.codes.ok):
    trace(f"GET {path}")
    reply = requests.get(f"{default_url()}{path}", headers=headers, params=params, verify=False)
    if reply.status_code == expected_code:
        return reply
    else:
        print(reply.content)


def requests_delete(path, params=None, headers=default_headers(), expected_code=requests.codes.no_content):
    trace(f"DELETE {path}")
    reply = requests.delete(f"{default_url()}{path}", headers=headers, params=params, verify=False)
    if expected_code:
        assert reply.status_code == expected_code
    return reply


def requests_post(path, json, headers=default_headers(), expected_code=requests.codes.created):
    trace(f"POST {path}")
    reply = requests.post(f"{default_url()}{path}", headers=headers, json=json, verify=False)
    if expected_code:
        assert reply.status_code == expected_code
    reply_json = reply.json()
    return reply


def requests_put(path, json, headers=default_headers(), expected_code=requests.codes.no_content):
    trace(f"PUT {path}")
    reply = requests.put(f"{default_url()}{path}", headers=headers, json=json, verify=False)
    if expected_code:
        assert reply.status_code == expected_code
    return reply
