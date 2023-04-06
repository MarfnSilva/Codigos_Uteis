import requests



import requests, json, traceback, sys
#from WAccessApiClient import createUser
#from testeimport import createUser_2

try:

    print('try')
    url = "https://2n3gjx2wue-vpce-005982e4f40293b4f.execute-api.us-east-2.amazonaws.com/prod/v1/"
    #url = 'https://2n3gjx2wue.execute-api.us-east-2.amazonaws.com/prod'

    auth_endpoint = 'authentication'
    
    print('url')
    proxies = {"http": "http://proxy.adhosp.com.br:8080"}

    payload = "{\r\n  \"username\": \"invenzi\",\r\n  \"password\": \"#407107Adm#\"\r\n}"
    headers = {
        'x-api-key': 'lAid2UFGAiarvPYY44IYr4caqKCVNNBx87HVxNin',
        'Content-Type': 'application/json'
    }

    response = requests.put(url + 'authentication', headers=headers, data = payload)
    #response = requests.put(url + auth_endpoint, headers=headers, proxies=proxies, data = payload)
    
    reply_json = response.json()
    #print(response)
    #print(response.content.decode())
    id_token = reply_json['id_token']

    #print(id_token)

    headers_2 = {
        'x-api-key': 'lAid2UFGAiarvPYY44IYr4caqKCVNNBx87HVxNin',
        'Content-Type': 'application/json',
        'Authorization' : id_token
    }

    reply = requests.get(url + f'atendimento', headers = headers_2, params=(("dt_atendimento", '08/06/2021'),("cd_multi_empresa", '8')))
    reply_json = reply.text
    print(reply_json)
    with open("exoport_file.txt", "a", encoding="utf-8") as newfile:
        #with open (folderName + '/trace.html', 'a', encoding="utf-8") as newfile:
        newfile.write(reply_json)
    #user = reply_json.get('Dados')
    #for atend in user:
    #    print(atend)

except Exception as ex:
    print(ex)
    traceback.print_exc(file=sys.stdout)