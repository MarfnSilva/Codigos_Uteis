# -*- coding: utf-8 # -*- 

import sys


waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

user_chid = int(sys.argv[1])
user_chtype = int(sys.argv[2])

if user_chtype == 1:
    print("Usuário Bloqueado")
    sys.exit(2)