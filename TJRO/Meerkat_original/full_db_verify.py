# -*- coding: utf-8 -*-

import requests, re
from meerkat_helpers import *


def get_wxs_users():
    get_user = requests_get('cardholders', params=(("CHType", 1),("CHType", 2),("CHType", 3),("CHType", 7),("CHType", 8),
                                            ("fields", "CHID,Firstname,CHType,CHState,Cards"),("includeTables", "Cards"), ("limit", 10000000)))
    get_user_json = get_user.json()
    cardholders_to_update = []
    for cardholder in get_user_json:
        ## By default user must be added to Meerkat server
        action = 'ADD'
        if cardholder["CHType"] not in settings["face_multi_factor_ch_types"]:
            ## Check if user need to be deleted from Meerkat Server
            print("Bypass - usuário sem dupla autenticação")
            action = 'DEL'
            #continue
        
        wxs_photo = requests_get(f'cardholders/{cardholder["CHID"]}/photos/1')
        wxs_photo = wxs_photo.json()
        if not wxs_photo or not cardholder["Cards"] or cardholder["CHState"] != 0:
            ## Check if user need to be deleted from Meerkat Server
            print('Usuario sem foto, sem cartão ou dasativado')
            action = 'DEL'
            #continue

        user_action = {
            "CHID": cardholder["CHID"],
            "action" : action
        }
        cardholders_to_update.append(user_action)
    
    return(cardholders_to_update)


def check_meerkat_users(wxs_users):
    for ip in settings["meerket_ip_servers"]:
        meerkat_ip_server = ip["meerkat_server_ip"]
        print(f'Working with server: {meerkat_ip_server}')
        app_key = ip["appKey"]
        if not app_key:
            continue
        
        headers = {
            'content-type': "application/json",
            'app_key': app_key
            }
        try:
            print(f'Get users from server: {meerkat_ip_server}')
            response = requests.get(meerkat_ip_server + 'faces', headers=headers, params=(("per_page", 200000),), timeout=15)
        except Timeout:
            print(f'********** Timeout getting users from server: {meerkat_ip_server}')
            continue
        else:
            if response.status_code != 200:
                print(f'**** Status Code not expected: {response.status_code}')
                continue

        response_json = response.json()
        person_faces_chid = []

        for face in response_json["faces"]:
            person_chid = re.sub('\D','',face["person_label"])
            person_faces_chid.append(int(person_chid))

        for user in wxs_users:
            if user["action"] == 'ADD':
                if user["CHID"] not in person_faces_chid:
                    wxs_photo = requests_get(f'cardholders/{user["CHID"]}/photos/1')
                    wxs_photo = wxs_photo.json()
                    enroll_face = {
                            "label": f'CHID_{user["CHID"]}',
                            "imageB64" : wxs_photo
                        }
                    enroll_user = requests.post(f'{meerkat_ip_server}/faces', headers={'content-type': 'application/json'}, json=enroll_face)
                    if enroll_user.status_code != 200:
                        print('Error')
                        continue
                    print(f'Face {enroll_face["label"]}: OK')

            if user["action"] == 'DEL':
                if user["CHID"] in person_faces_chid:
                    print(f'Deleting CHID: {user["CHID"]}')
                    del_headers = {
                        'content-type': "application/json",
                        'app_key': app_key
                        }

                    del_face = requests.delete(f'{meerkat_ip_server}/people/CHID_{user["CHID"]}', headers=del_headers)
                    print(del_face.text)

if __name__ == '__main__':
    wxs_users = get_wxs_users()
    check_meerkat_users(wxs_users)
