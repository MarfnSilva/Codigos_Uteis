# -*- coding: utf-8 -*-

import json, sys, requests
import datetime
from typing import Dict
from GenericTrace import *
from api_helpers import *

def get_driver_event(conn):
    get_event = conn.cursor()
    script = f"""
        SELECT
        [EventDateTime]
        ,[EventID]
        ,[ReaderID]
        ,[ReaderName]
        ,[CHID]
        ,[IdCorporate]
        ,[FirstName]
        ,[LinkedCHID]
        ,[ExpectedPlate]
        ,[LogArea6]
        FROM [W_Access_Events].[dbo].[WXS_Vopak_Area6]
        WHERE EventDateTime > DATEADD(minute, -5, getutcdate())
        AND LogArea6 is null
        ORDER BY EventDateTime DESC
        """
    get_event_ = get_event.execute(script)
    
    # ---------- If no results bypass --------------
    if get_event_.rowcount == 0:
        trace('Nenhum resultado', color='DarkOrange')

    readers_row = []
    for event_date_time, event_id, reader_id, reader_name, chid, id_corporate, name, linked_chid, expected_plate, log_area_6 in get_event_.fetchall():
        if reader_id in readers_row:
            # ---------- Desconsidera as demais linhas caso já tenha retornado algum evento --------------
            trace(f'Desconsiderar evento pois houve um acesso mais recente | ReaderID {reader_id}', color='DarkOrange')
            set_event_property(event_id, 'Veiculo sem registro de acesso')

        trace(f'Get IDCorporate: {id_corporate} and Expected Plate: {expected_plate}', color='DarkOrange')

        tolerance_plate = valid_plate_tolerance_seconds(event_date_time)
        if tolerance_plate == 2:
            trace('Tolerancetime expired, getting any plate.', color='DarkOrange')
            expected_plate = None
        
        elif tolerance_plate == 1:
            reg_mov_json = registra_movimento_json(id_corporate, reader_name, event_date_time, reader_id, expected_plate, 'https://10.112.25.7/W-Access/plate_not_found.png' )
            response = True#call_corporate(reg_mov_json)
            trace(reg_mov_json)

            # if response.status_code == requests.codes.ok:
            if response:
                trace('Writing Log')
                set_event_property(event_id, 'Motorista sem registro de trânsito do veículo')
            continue
            
        wxs_event = check_last_events(event_date_time, reader_id, expected_plate)
        if wxs_event:
            lpr_url_image = get_lpr_image(wxs_event["EventID"])

            if lpr_url_image:
                reg_mov_json = registra_movimento_json(id_corporate, reader_name, event_date_time, wxs_event["SourceID"], wxs_event["ClearCode"], lpr_url_image )
                response = True#call_corporate(reg_mov_json)
                trace(reg_mov_json)

                # if response.status_code == requests.codes.ok:
                if response:
                    trace('Writing Log')
                    set_event_property(event_id, 'Envio Corporate OK')

         
        readers_row.append(reader_id)


def check_last_events(event_date_time, reader_id, expected_plate=None):
    lpr_name_list = get_readers(reader_id)
    for reader_name in lpr_name_list:
        _, reply_json = get(f'events', params=(("eventType", 1),("minEventDateTime", event_date_time),("sourceName", reader_name)))
        
        for event in reply_json:
            if not expected_plate:
                trace(f'Event found with eventID: {event["EventID"]} | Reader: {event["SourceName"]} | Plate: {event["ClearCode"]} ')
                return(event)
            
            if event["ClearCode"] == expected_plate:
                trace(f'Event found with eventID: {event["EventID"]} | Reader: {event["SourceName"]} | Plate: {event["ClearCode"]} ')
                return(event)
    
    trace('Nenhum evento encontrado')
    return None

    
if __name__ == '__main__':
    trace("Integração Vopak: v2.00", color='Gold')
    conn = None
    while True:
        trace('nova iteração', color="Orange")
        if not conn:
            conn = sql_connect(conn)
        if conn:
            get_driver_event(conn)

        #sys.exit()
        time.sleep(1)