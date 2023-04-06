import requests

url = "http://localhost/W-AccessAPI/v1/"
h = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180' }

# list_chid = (8441, 8426)


# DELETA TODOS
reply = requests.get(url + 'cardholders', headers=h, params=(("limit", 20000),))
reply_json = reply.json()

for user in reply_json:#list_chid:
    # if user["CHType"] != 1:
    del_user = requests.delete(url + f'cardholders/{user["CHID"]}', headers=h)
    if del_user.status_code == requests.codes.no_content:
        print(f"Usuário Deletado - CHID " + str(user["CHID"]))
    else:
        print("Error: " + del_user.json()["Message"])
    

#------------------------------------------------------------------------------------------#


# DELETA USUÁRIOS SEM FOTO
reply = requests.get(url + 'cardholders', headers=h, params=(("CHType", 1), ("limit", 20000)))
reply_json = reply.json()

for user in reply_json:
    reply = requests.get(url + f'cardholders/{user["CHID"]}/photos/1', headers=h)
    foto_json = reply.json()

    if not foto_json:
        del_user = requests.delete(url + f'cardholders/{user["CHID"]}', headers=h)
        if del_user.status_code == requests.codes.no_content:
            print(f"Usuário Deletado - CHID " + str(user["CHID"]))
        else:
            print("Error: " + del_user.json()["Message"])
        
        #print(str(user["CHID"]) +' - '+ del_user.reason)
    else:
        print("Usuário Possui Foto - CHID " + str(user["CHID"]))