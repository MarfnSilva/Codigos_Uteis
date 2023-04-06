from pyrsistent import CheckedType
import requests#, sys, pyodbc
#from requests.models import Response


waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
url = 'http://localhost/W-AccessAPI/v1/'
h = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}


chid = 7
chtype = 2

reply = requests.get(url + f'cardholders/{chid}', headers=h, params=(("chtype",{chtype}),))
wxs_users = reply.json()


if wxs_users["AuxText01"]:
    print('Tem RG')
    print(wxs_users["AuxText01"])

else:
    print('N tem RG')
    print(wxs_users["AuxText01"])