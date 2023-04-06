# -*- coding: utf-8 -*-

import pyodbc, requests, json, sys
from GenericTrace import *


url = "http://localhost/W-AccessAPI/v1/"
h = { 'WAccessAuthentication': 'salvar:#integra#', 'WAccessUtcOffset': '-180' }



def generate_plate(plate):
    reply = requests.get(url + 'cards/licensePlates/cardNumber', headers=h, params=(("licensePlateText", plate),))
    card_plate = reply.json()
    return(card_plate)

def assign_card_plate(wxs_user, card_plate):

    new_card = { "ClearCode": wxs_user["FirstName"], "CardNumber": card_plate, "FacilityCode": 0, "CardType": 0, "PartitionID": 0, "IsAutomaticCard": True }
    get_card = requests.get(url + 'cards', headers=h, params=(("limit", 30000),("ClearCode", wxs_user["FirstName"])))
    if get_card.status_code == requests.codes.not_found:
        card = create_card(new_card)
    elif get_card.status_code == requests.codes.ok:
        card = get_card.json()

    assign_card = requests.post(url + f'cardholders/{wxs_user["CHID"]}/cards', headers=h, json=card, params=(("callAction", False),))
    
def assign_access_level(wxs_user):
    reply = requests.post(url + f'cardholders/{wxs_user["CHID"]}/accessLevels/287', headers=h, json={}, params=(("callAction", False),))

def associate_to_cardholder(chid, card_chid):
    linked = { "CHID": chid, "LinkedCHID": card_chid, "EscortsLinkedCH": False, "EscortedByLinkedCH": False }
    reply = requests.post(url + f'cardholders/{chid}/linkedCardholders', headers=h, json=linked, params=(("callAction", False),))

def remove_field_content(chid):
    trace(chid)
    reply = requests.get(url + f'cardholders/{chid}', headers=h)
    cardholder = reply.json()
    trace(f'Remove field content from user: {cardholder["CHID"]} | FirstName: {cardholder["FirstName"]}')
    cardholder["AuxText10"] = ''
    cardholder["AuxText11"] = ''
    cardholder["AuxText12"] = ''
    cardholder["AuxText13"] = ''
    reply = requests.put(url + 'cardholders', headers=h, json = cardholder, params=(("callAction", False),))
    if reply.status_code in [ requests.codes.ok, requests.codes.no_content ]:
        trace('Cardholder updated')
    else:
        trace(reply.content, reply.status_code)
        

def create_card(new_card):
    trace(f'Creating new card.')
    create_card = requests.post(url + 'cards', headers=h, json=new_card, params=(("callAction", False),))
    card = create_card.json()
    if card:
        trace(f'Card created with cardID = {card["CardID"]}')
        return(card)
    else:
        trace(f'Error creating card with clearcode = {new_card["ClearCode"]}')