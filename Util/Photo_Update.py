# -*- coding: utf-8 -*-
import requests, sys, pyodbc

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

with open("photo1.jpg", "rb") as foto:
    reply = requests.put(waccessapi_endpoint + 'cardholders/2/photos/1', files=(("photoJpegData", foto), ), headers=waccessapi_header)
    if reply.status_code in [ requests.codes.ok, requests.codes.no_content ]:
        print("Cardholder photo 1 update OK")
    else:
        print(f"Error: {str(reply)} " + str(reply.json()["Message"]))