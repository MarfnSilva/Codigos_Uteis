
import request, sys 




url = "http://localhost/W-AccessAPI/v1/"
h = { 'WAccessAuthentication': 'send_email:#407107Adm#', 'WAccessUtcOffset': '-180' }


reply = requests.get(url + f'cardholders/{CHID}',headers=h)
cardholders = reply.json()

