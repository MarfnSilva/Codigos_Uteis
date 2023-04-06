

import requests, json, sys


def assign_access_level(url, h, contact_user, wxs_chid):  
    unid_internacao = contact_user["AuxLst04"]

    get_combo = requests.get(url + f'chComboFields', headers=h, params=(("CHType", 8),("fieldID", "lstBDA_AuxLst04"),("comboIndex", unid_internacao)))
    get_combo_json = get_combo.json()

    for item in get_combo_json:
        unid_internacao_dsc = item["strLanguage2"]
        continue

    get_access = requests.get(url + f'accessLevels', headers=h)
    get_access_json = get_access.json()

    for access in get_access_json:
        if access["AccessLevelName"] == unid_internacao_dsc:
            assign_access = requests.post(url + f'cardholders/{wxs_chid}/accessLevels/{access["AccessLevelID"]}', headers=h, json={})
            