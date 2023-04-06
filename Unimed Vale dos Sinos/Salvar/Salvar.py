# -*- coding: utf-8 -*-


# create exe: pyarmor pack --options " -D" Salvar.py

import pyodbc, requests, json, traceback, sys, os
from datetime import datetime  
from datetime import timedelta 
from GenericTrace import *
from requests import Response


url = "http://localhost/W-AccessAPI/v1/"
h = { 'WAccessAuthentication': 'salvar_API:#integra#', 'WAccessUtcOffset': '-180' }


try:
    
    wxs_chid = sys.argv[1]
    wxs_chtype = sys.argv[2]
    wxs_chstate = sys.argv[3] # na liberação da visita recebemos uma caractere 't' para que a ação não seja executada
    wxs_action = sys.argv[4] # libera ou salvar
    wxs_chk03 = sys.argv[5] # Checkbox de liberação da saída
    #wxs_chid = '23220'
    #wxs_chtype = '1'
    #wxs_chstate = '0'
    #wxs_action = 'salvar'
    #wxs_chk03 = True

    visitor_accesslevel = '99'
    resident_accesslevel = '98'

    def assign_accessLevel(url, h, wxs_chid, visitor_accesslevel):

        print("Assign Access Level")
        chAccessLevel = { "CHID" : wxs_chid, "AccessLevelID": visitor_accesslevel , "AccessLevelStartValidity": None , "AccessLevelEndValidity": None}
        print(chAccessLevel)
        reply = requests.post(url + f'cardholders/{wxs_chid}/accessLevels/{visitor_accesslevel}', json=chAccessLevel, headers=h, params=(("callAction", False),))
        if reply.status_code == requests.codes.not_found:
            trace("** error")
            trace(reply.content)
        else:
            trace(reply.content)
            trace("Access Level Assigned")

    trace(str(datetime.now())[:-3])
    trace(f'** New visit: {str(datetime.now())[:-3]}')
    trace(f'Usuário: {wxs_chid} - parameter_type : {type(wxs_chid)}')
    trace(f'CHType: {wxs_chtype} - parameter_type : {type(wxs_chtype)}')
    trace(f'CHState: {wxs_chstate} - parameter_type : {type(wxs_chstate)}')
    trace(f'Action: {wxs_action} - parameter_type : {type(wxs_action)}')
    trace(f'Liberar saída: {wxs_chk03} - parameter_type: {type(wxs_chk03)}')
    #trace('parameter_type: ' + type(wxs_chk03))

    if wxs_chtype == '1' and wxs_action == 'libera':
        trace("entrou no loop de liberação de visitas - Visitante : Liberar")
        assign_accessLevel(url, h, wxs_chid, visitor_accesslevel)

    elif (wxs_chtype == '1') and (wxs_action == 'salvar') and (wxs_chstate == '0'):
        trace("entrou no loop de liberação de visitas - Visitante : Salvar")
        trace(f'Chckbox liberar visita = {wxs_chk03}')
        if wxs_chk03 == 'True':
            assign_accessLevel(url, h, wxs_chid, visitor_accesslevel)

    elif wxs_chtype in ('2', '3', '5', '6') and wxs_action == 'salvar' :
        trace("entrou no loop chtype Residentes")

        get_accessLevel = requests.get(url + 'cardholders/' + wxs_chid + '/accessLevels/' + resident_accesslevel,  headers=h)
        if get_accessLevel.status_code == requests.codes.not_found:
            chAccessLevel = { "CHID" : wxs_chid, "AccessLevelID": resident_accesslevel , "AccessLevelStartValidity": None , "AccessLevelEndValidity": None}
            assignAccessLevel = requests.post(url + 'cardholders/' + str(wxs_chid) + '/accessLevels/' + str(resident_accesslevel), json=chAccessLevel, headers=h, params=(("callAction", False),))
    
    else:
        trace("Nenhuma condição atendida")

except Exception as ex:
    print(ex)
    trace(ex)
    #writeTrace('', ex)
    traceback.print_exc(file=sys.stdout)