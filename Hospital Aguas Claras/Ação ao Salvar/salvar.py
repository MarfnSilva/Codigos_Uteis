# -*- coding: utf-8 -*-

import pyodbc, requests, json, sys
from GenericTrace import *
from salvar_client import *

url = "http://localhost/W-AccessAPI/v1/"
h = { 'WAccessAuthentication': 'salvar:#integra#', 'WAccessUtcOffset': '-180' }

# Visitor data
chtype = int(sys.argv[1]) # AuxText10 (Placa)
chid = int(sys.argv[2])
placa = sys.argv[3] # AuxText12 (Placa)
marca = sys.argv[4] # AuxText11 (Marca)
modelo = sys.argv[5] # AuxText13 (Modelo)
cor = sys.argv[6] # AuxText10 (Cor)


# -------------------------------Testes --------------------------------
# chtype = 2 # CHtype 
# chid = 64 # CHID
# placa = 'PBY-3590'.replace('-','') # AuxText10 (Placa)
# marca =  'CHEVROLET' # AuxText11 (Marca)
# modelo = 'ONIX' # AuxText12 (Modelo)
# cor = 'Cinza' # AuxText13 (Cor)
# -------------------------------Testes --------------------------------


## ---------------------------- Begin - Create and associate vehicle to cardholder --------------------------------------

if chtype not in (2, 5, 6): # Colaboradores, Prestadores e Médicos
    trace(f'CHType not in (2, 5, 6), end process')
    sys.exit()

if placa:
    placa = placa.replace('-', '')
    get_vehicle = requests.get(url + 'cardholders', headers=h, params=(("nameSearch", placa),("CHType", 4),("includeTable", "Cards")))
    get_vehicle = get_vehicle.json()


    if get_vehicle:
        trace('Carro encontrado')
        for wxs_user in get_vehicle:
            trace(f'Placa: {wxs_user["FirstName"]}')
            card_plate = generate_plate(placa)
            assign_card_plate(wxs_user, card_plate)
            assign_access_level(wxs_user)
            associate_to_cardholder(chid, wxs_user["CHID"])
            remove_field_content(chid)
        
    else:
        trace('Carro não encontrado')
        new_car = { "FirstName": placa, "CHType": 4, "PartitionID": 1, "AuxText01": marca, "AuxText02" : modelo, "AuxText03" : cor}

        reply = requests.post(url + 'cardholders', headers=h, json=new_car, params=("callAction", False))
        reply_json = reply.json()
        print(reply_json)
        if reply.status_code == requests.codes.created:
                trace(f"New CHID: {reply_json['CHID']}")
                wxs_user = reply_json
                card_plate = generate_plate(placa)
                assign_card_plate(wxs_user, card_plate)
                assign_access_level(wxs_user)
                associate_to_cardholder(chid, wxs_user["CHID"])
                remove_field_content(chid)

        else:
            trace("Error: " + reply_json["Message"])
## ---------------------------- END - Create and associate vehicle to cardholder --------------------------------------


# ## ---------------------------- Begin - Create/Assign Card to Cardholder --------------------------------------
'''
14/07/2021 : Conforme conversas com o Rodrigo Ferraz (Hospital Aguas Claras) não faremos a criação automatica dos cartões de residente: Medicos, prestadores e colaboradores.

'''
# trace(f'User chtype = {chtype}, check if user has an assigned card.')
# cardholder = requests.get(url + f'cardholders/{chid}', headers=h, params=(("includetables", "Cards"),))
# cardholder_json = cardholder.json()
# #print(cardholder.content, cardholder_json)

# if not cardholder_json["Cards"]:
#     trace(f'User chid = {chid} dont has an assigned card. Check if card exists.')
#     card_name = str(cardholder_json["CHID"])
#     card_name = f'CARD_{card_name.zfill(9)}'       
#     print(card_name)
#     get_card = requests.get(url + f'cards', headers=h, params=(("ClearCode", card_name),))
#     get_card_json = get_card.json()
#     #print(get_card_json)
#     if get_card.status_code == requests.codes.not_found:
#         trace(f'Card {card_name} dont exists. Creating new card.')
#         new_card = { "ClearCode": card_name, "CardNumber": chid + 2000000, "FacilityCode": 0, "CardType": 0, "PartitionID": 0, "IsAutomaticCard": True }
#         card = create_card(new_card)
#     elif get_card.status_code == requests.codes.ok:
#         card = get_card.json()
#     else:
#         trace("Error: " + get_card_json["Message"])

#     trace('Assign card to cardholder')
#     assign_card = requests.post(url + f'cardholders/{cardholder_json["CHID"]}/cards', headers=h, json=card, params=(("callAction", False),))
#     #print(assign_card.status_code)
#     if assign_card.status_code == 201:
#         trace(f'Card assigned')
#     else:
#         trace('Error creating card.')

# else:
#     trace(f'Card is already assigned to cardholder.')

# ## ---------------------------- END - Create/Assign Card to Cardholder --------------------------------------