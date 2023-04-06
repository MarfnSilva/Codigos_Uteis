# -*- coding: utf-8 -*-

import json

global settings
settings = json.loads(open('settings.json').read())

def id_gerenciador():
    global settings
    return settings["id_gerenciador"]

def leitoras():
    global settings
    return settings["leitoras"]

def options():
    global settings
    return settings["options"]

def servername():
    global settings
    return settings["servername"]

def userid():
    global settings
    return settings["userid"]

def password():
    global settings
    return settings["password"]

def databasename():
    global settings
    return settings["databasename"]

def odbcdriver():
    global settings
    return settings["odbcdriver"]

