# -*- coding: utf-8 -*-

import requests, json, xmltodict, threading
from base64 import b64encode
from GenericTrace import report_exception, trace
from datetime import datetime, timedelta

from requests.auth import HTTPDigestAuth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

global settings
settings = json.loads(open('settings.json').read())

def lpr_server_ip():
    global settings
    return settings["lpr_server_ip"]

def lpr_server_port():
    global settings
    return settings["lpr_server_port"]

def lpr_server_user():
    global settings
    return settings["lpr_server_user"]

def lpr_server_pass():
    global settings
    return settings["lpr_server_pass"]

def lpr_server_hostname():
    global settings
    return settings["lpr_server_hostname"]

def wxs_site_controller_ip():
    global settings
    return settings["SiteControllerIP"]

def wxs_site_controller_port():
    global settings
    return settings["SiteContollerPort"]

def poll_lpr(session, session_id):
    try:
        trace(f"Polling Avigilon Server - IP: {lpr_server_ip()}")
        url = f"https://{lpr_server_ip()}:{lpr_server_port()}/mt/api/rest/v1/events/search?session=" + session
        body = { 
            "queryType": "ACTIVE",
            "serverId": session_id
        }
        requests.get(url, params=body, timeout=15, headers={ "Content-Type": "application/json" }, verify=False)
    except Exception as ex:
        trace(ex)

def polling(session, session_id):
    try:
        new_thread = threading.Thread(target=poll_lpr, args=(session, session_id, ))
        new_thread.start()
    except:
        trace(f"POLL process Error", color="red")

def send_event_to_sitecontroller(reader_name, plate, plate_image):
    trace("Sending LPR event to siteController", color="Turquoise")
    username = "axxon"
    password = "q8M5Ny4RV55ZxgJj"

    headers = {
        "Authorization": "Basic YXh4b246cThNNU55NFJWNTVaeGdKag==",
        "Content-Type": "application/json"
    }

    data = {
        "source_type" : "AXXON_Intellect",
        "event_type" : "lpr",
        "source_identification" : reader_name,
        "plate" : plate,
        "image_bytes" : plate_image
    }
    url = f"https://{wxs_site_controller_ip()}:{wxs_site_controller_port() + 2}/events"
    reply = requests.post(url, headers=headers, json=data, verify=False)
    trace(f'Site Controller reply status: {reply.reason}', color='Turquoise')
