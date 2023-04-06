# -*- coding: utf-8 -*-

import requests, sys
import smtplib
from email.message import EmailMessage
from requests.sessions import extract_cookies_to_jar
from GenericTrace import *
import configparser

parser = configparser.ConfigParser()
parser.read("send_email.cfg")
email_remetente = parser.get("config", "remetente")
smtp = parser.get("config", "smtp")
smtp_port = parser.get("config", "smtp_port")
login = parser.get("config", "login")
token = parser.get("config", "token")
company = parser.get("config", "company")

parametro = '17' # argumento q veio da ação

if parametro in (company):
    print("enviar email")
else:
    print("Email n enviado")
