import pyodbc, requests, json, sys, configparser


waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

# teste={
#   "CHID": 7,
#   "LinkedCHID": 7932,
#   "EscortsLinkedCH": True,
#   "EscortedByLinkedCH": True
# }

# user_post = requests.post(waccessapi_endpoint + 'cardholders/7/linkedCardholders', json=teste, headers=waccessapi_header, params=(("callAction", False),))
# user_port_json = user_post.json()
chid= 10
card_name= str(chid)
card_name = f'BIO_2{card_name.zfill(9)}'
card_number = 200000000+chid 
print(card_name)
print(card_number)
