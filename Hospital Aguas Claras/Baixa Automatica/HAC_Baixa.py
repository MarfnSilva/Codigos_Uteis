# -*- coding: utf-8 -*-

import requests, json, sys


waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

wxs_chtype = int(sys.argv[1]) 
wxs_visitor_type = int(sys.argv[2])
wxs_temp_acomp = sys.argv[3]
contact_chid = sys.argv[4]
wxs_chid = sys.argv[5]

if wxs_chtype == 1:
    if wxs_visitor_type != 1:
        delvisit = requests.delete(waccessapi_endpoint + f'cardholders/{wxs_chid}/activeVisit', headers=waccessapi_header, params=(("callAction", False),))
    else:
        get_visit = requests.get(waccessapi_endpoint + f'cardholders/{contact_chid}/activeVisit', headers=waccessapi_header, params=(("callAction", False),))
        get_visit_json = get_visit.json()
        if not get_visit_json:
            delvisit = requests.delete(waccessapi_endpoint + f'cardholders/{wxs_chid}/activeVisit', headers=waccessapi_header, params=(("callAction", False),))
else:
    sys.exit(0)