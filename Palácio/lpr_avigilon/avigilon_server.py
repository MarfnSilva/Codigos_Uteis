import datetime
import hashlib
import json
import requests
import threading
import secrets
import base64
import datetime

from requests.auth import HTTPDigestAuth
from flask import Flask, request, json, abort
from flask_apscheduler import APScheduler
from helper import *

app = Flask(__name__)
scheduler = APScheduler()


@app.before_request
def before_request():
    try:
        data = request.data
        info = f"{dict(request.args)} {dict(request.form)} len={len(data)} {data}"
        trace_msg = f"Avigilon WS: {request.method} {request.path} {info}"
        event_data = json.loads(data.decode("utf-8"))
        # trace(event_data)
        trace(trace_msg)
        
        event_type = event_data.get("type")
        if event_type in ["HELLO", "HEART"]:
            return "200"
        elif event_type == "NOTIFICATION":
            notification = event_data["notifications"][0]
            if notification["event"]["type"] == "DEVICE_LPR_PLATE_FOUND":
                license_plate = notification["event"]["licensePlate"]
                reader_name = notification["event"]["location"]
                cameraId = notification["event"]["cameraId"]

                trace(f"SENDING INFO TO SITE CONTROLLER: plate: {license_plate}, reader: {reader_name}")

                url = f"https://{lpr_server_ip()}:{lpr_server_port()}/mt/api/rest/v1/media?session=" + session
                body = {
                    "cameraId": cameraId,
                    "format": "jpeg",
                    "frames": "all",
                    "media": "video",
                    "t": "live"
                }
                plate_image = requests.get(url, params=body, headers={"Content-Type": "application/json"}, timeout=(2,200), verify=False)
                plate_image64 = base64.b64encode(plate_image.content).decode("utf-8")
                trace(f"Image Base64: {plate_image64}")

                send_event_to_sitecontroller(reader_name, license_plate, plate_image64)
            return "200"
        else:
            return "400"

    except Exception as ex:
        report_exception(ex)
        # abort(500)
        return

if __name__ == "__main__":

    url = f"https://{lpr_server_ip()}:{lpr_server_port()}/mt/api/rest/v1/"
    h = { "Content-Type": "application/json" }

    timestamp = int(datetime.timestamp(datetime.now()))
    userNonce = "0014y00002jvUI5AAM"
    userKey = "b60e7882f15ef41ea795b1dfd83aff2dc7ad4efda3349edd69c3b4c5122edc6a"

    encrypted = hashlib.sha256(f"{timestamp}{userKey}".encode("utf-8")).hexdigest()
    authToken = f"{userNonce}:{timestamp}:{encrypted}" 

    login = {
        "username": lpr_server_user(),
        "password": lpr_server_pass(),
        "clientName": lpr_server_hostname(),
        "authorizationToken": authToken # "0014y00002jvUI5AAM:1662662826:29b881c97056d05607bbb9e2528347741dbf196c47abcfdbe65e51226b366026",
    }
    reply = requests.post(url + "login", json=login, headers=h, verify=False)

    reply_json = reply.json()
    if reply.status_code == requests.codes.ok:
        global session
        session = reply_json["result"]["session"]
    else:
        trace(reply_json)
        if reply_json["message"] != 'Not Found':
            trace("Error: " + reply_json["message"] + reply_json["meta"])

    reply = requests.get(url + "webhooks?session=" + session, headers=h, verify=False)
    reply_json = reply.json()
    if reply.status_code == requests.codes.ok:
        if reply_json["result"]["webhooks"]:
            for webhook in reply_json["result"]["webhooks"]:
                created_webhooks = webhook["id"]

                delete_webhooks = {
                    "session": session,
                    "ids": [ created_webhooks ]
                }
                reply = requests.delete(url + "webhooks?session=" + session, json=delete_webhooks, headers=h, verify=False)
                reply_json = reply.json()
                if reply.status_code == requests.codes.ok:
                    trace(f"Webhook: {created_webhooks} deleted")
                else:
                    trace(reply_json)
                    if reply_json["message"] != 'Not Found':
                        trace("Error: " + reply_json["message"] + reply_json["meta"])
    else:
        trace(reply_json)
        if reply_json["message"] != 'Not Found':
            trace("Error: " + reply_json["message"] + reply_json["meta"])
    
    crypto = secrets.token_bytes(16)
    authenticationToken = base64.b64encode(crypto).decode("utf-8")

    trace(f"SESSION: {session}")
    webhook = {
        "session": session,
        "webhook": {
            "url": f"http://{wxs_site_controller_ip()}:5443",
            "heartbeat": {
                "enable": True,
                "frequencyMs": 30000
            },
            "authenticationToken": authenticationToken,
            "eventTopics": { 
                "whitelist": [ "ALL" ] 
            }
        }
    }
    
    reply = requests.post(url + "webhooks", json=webhook, headers=h, verify=False)
    reply_json = reply.json()
    if reply.status_code == requests.codes.ok:
        session_id = reply_json["result"]["id"]
    else:
        trace(reply_json)
        if reply_json["message"] != 'Not Found':
            trace("Error: " + reply_json["message"] + reply_json["meta"])

    # WEBHOOK #
    scheduler.add_job(id="Scheduled Task", func=polling, trigger="interval", seconds=30, args=(session, session_id, ))
    scheduler.start()

    app.run(host=wxs_site_controller_ip(), port=5443, debug=True)
