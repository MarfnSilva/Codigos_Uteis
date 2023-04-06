# -*- coding: utf-8 -*-

import requests, sys
import smtplib
from email.message import EmailMessage
from requests.sessions import extract_cookies_to_jar
from GenericTrace import *
import configparser



trace('Start new visit')

url = "http://localhost/W-AccessAPI/v1/"
h = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180' }

def send_email(email):
    parser = configparser.ConfigParser()
    parser.read("send_email.cfg")
    email_remetente = parser.get("config", "remetente")
    smtp = parser.get("config", "smtp")
    smtp_port = parser.get("config", "smtp_port")
    login = parser.get("config", "login")
    token = parser.get("config", "token")
    teste = str(parser.get("config", "teste"))

    trace('Enviando Email')
    # Mensagem a ser enviada.
    msg = EmailMessage()
    #msg.set_content('Prezado;\n \n \n Informamos que você excedeu a cota máxima de visitantes em Aratu - Iate Clube, a partir do próximo será cobrada uma taxa por visitante!')
    msg.set_content(f'''<!DOCTYPE html>
                        <html>
                            <body>
                                <div style="background-color:#C1BFBF;padding:10px 20px;height: 60px;width:400px">
                                    <h2 style="font-family:Georgia, 'Times New Roman', Times, serif;color:red;text-align:center">Aratu - Iate Clube</h2>
                                </div>
                                <div>
                                    <div style="height: 500px;width:400px;background-color:#F5F4F4; padding:20px">
                                        <div style="text-align:center;">
                                            <h3>Article 1</h3>
                                            <p>Prezado;</p>
                                            <p>Informamos que você excedeu a cota máxima de visitantes em Aratu - Iate Clube, a partir do próximo será cobrada uma taxa por visitante!</p>
                                            <p>{cardholders["EMail"]}</p>
                                            <a href="#">Read more</a>
                                        </div>
                                    </div>
                                </div>
                            </body>
                        </html>''', subtype='html')
    # Assunto , remetente e destinatario.
    msg['Subject'] = 'Aratu - Iate Clube'
    msg['From'] = email_remetente
    msg['To'] = email
    trace(f'Email enviado para destinatário: {email}')
    # Envio da mensagem atráves do servidor SMTP.
    server = smtplib.SMTP_SSL(smtp, smtp_port)
    server.login(login, token)
    server.send_message(msg)
    server.quit()
    

#contact_chid = sys.argv[1]
contact_chid = 118 
trace(f'Parametros recebidos: {contact_chid}')

reply = requests.get(url + f'cardholders/{contact_chid}',headers=h)
cardholders = reply.json()
#trace(cardholders)
trace(f'Nova visita iniciada para o usuário {cardholders["FirstName"]}')

#se for maior que zero subtrair 1

if cardholders["MaxTransits"]:
    trace(f'Usuário possui {cardholders["MaxTransits"]} emails.')
    if cardholders["MaxTransits"] > 0:
        cardholders["MaxTransits"] = cardholders["MaxTransits"] - 1
        user = requests.put(url + f'cardholders',headers=h,json = cardholders)
        
    # se for igual a 0 ou menor enviar e-mail
    elif cardholders["MaxTransits"] <= 0: 
        trace(f'O usuário não possui mais créditos de liberação de visita.')
        send_email(cardholders["EMail"])

    trace(cardholders["MaxTransits"])

else:
    send_email(cardholders["EMail"])
    trace(f'Usuário não possui mais crédito de email.')