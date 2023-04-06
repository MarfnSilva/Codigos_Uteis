# -*- coding: utf-8 -*-
# pyarmor pack --options " -F" atualiza_meerkat.py

import requests, time
from datetime import datetime, timedelta

url = "http://localhost/W-AccessAPI/v1/"

h = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180' }

reply = requests.get(url + 'cardholders', headers=h, params=(("CHType", 2),("CHType",3), ("limit", 5000000)))
reply_json = reply.json()

initial_time = datetime.now()

n = 0
for user in reply_json:
    try:
        send = requests.put(url + 'cardholders', headers=h, json=user)
        time_now = datetime.now()
        delta = time_now - initial_time
        print(f'{delta} - {n} - Atualização do usuário: {user["FirstName"]}  | Status: {send.reason}')
        n += 1
        time.sleep(0.5)

    except Exception as ex:
        with open ('import_error.txt', 'a', encoding="utf-8") as newfile:
            newfile.write(ex)

