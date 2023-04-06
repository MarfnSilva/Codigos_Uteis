# -*- coding: utf-8 -*-

import requests, sys, configparser, datetime

waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}


n = 1100000001
i = 1
for card in range(3000):
    card_name = str(n).zfill(4)
    card_name = f'VIS_{i}' 
    new_card = { "ClearCode": card_name, "CardNumber": n, "FacilityCode": 0, "CardType": 1, "PartitionID": 0, "IsAutomaticCard": False }
    get_card = requests.get(waccessapi_endpoint + f'cards', params=(("limit", 1),("ClearCode", card_name)))
    get_card_json = get_card.json()
    
    if not get_card_json:
        create_card = requests.post(waccessapi_endpoint + f'cards', json=new_card)
        created = create_card.json()
        if created:
            print (f'Cartão {card_name} Criado com Sucesso')
        else:
            print(f'Erro ao Criar o Cartão {card_name}')

    else:
        print(f'Cartão {card_name} já existe')

    n += 1
    i += 1