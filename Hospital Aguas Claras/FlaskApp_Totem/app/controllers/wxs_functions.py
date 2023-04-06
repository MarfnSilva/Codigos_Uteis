
import requests
from app.controllers.connection import *
from app.controllers.GenericTrace import *


def check_contact(visitor):
    reply = requests_get(f'cardholders/{visitor["LastVisit"]["ContactCHID"]}', params=(("CHType", 8), ("includeTables", "ActiveVisit,LastVisit")))
    contact = reply.json()
    if contact["AuxLst04"]:
        get_unid = requests_get('chComboFields', params=(("CHType", 8),("FieldID", "lstBDA_AuxLst04"),("ComboIndex", contact["AuxLst04"])))
        get_unid_json = get_unid.json()
        for item in get_unid_json:
            unid_int = item["strLanguage2"]
    else:
        unid_int = None

    leito = contact["AuxText13"]
    
    if not contact["ActiveVisit"]:
        h1 = f'Dirija-se à recepção'
        txt = f'O paciente {contact["FirstName"]} não pode receber visitas no momento.'
        print(h1, txt)
        return(h1, txt, leito, unid_int)

    else:
        if visitor["ActiveVisit"]:
            if leito:
                txt = f'O paciente encontra-se no leito {leito} na unidade de internação [{unid_int}]. A visita está liberada até HH:MM, caso tenha dúvida...'
            else:
                txt = f'O paciente encontra-se na ...... [ Definir o texto ]'
            
            h1 = f'Visita liberada'
            print(h1, txt, leito, unid_int)
            return(h1, txt, leito, unid_int)
        else:
            return(None,None, leito, unid_int)


def check_user(cpf):
    reply_1 = requests_get('cardholders', params=(("IdNumber", cpf),("CHType", 1), ("includeTables", "ActiveVisit,LastVisit")))
    reply_json1 = reply_1.json()
    cpf_mask = '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])
    reply_2 = requests_get('cardholders', params=(("IdNumber", cpf_mask),("CHType", 1), ("includeTables", "ActiveVisit,LastVisit")))
    reply_json2 = reply_2.json()
    reply_json = reply_json1 + reply_json2
    if reply_json:
        for visitor in reply_json:
            print(visitor["FirstName"])
            if visitor["LastVisit"]:
                contact_chid = visitor["LastVisit"]["ContactCHID"]
                h1,txt,leito,unid_int = check_contact(visitor)
                if not txt:
                    cardnumber = visitor["CHID"]
                    clearcode = f'BIO_{str(cardnumber).zfill(9)}'   
                    new_visit = {"CHID": cpf, "FirstName" : visitor["FirstName"], "ClearCode" : clearcode, "ContactCHID" : contact_chid}
                    reply = requests_post(f'cardholders/{visitor["CHID"]}/activeVisit', json=new_visit)
                    print(reply.content)
                    if leito:
                        txt = f'O paciente encontra-se no leito {leito} na unidade de internação [{unid_int}]. O horário das visitas são .... '
                    else:
                        txt = f'O paciente encontra-se na ...... [ Definir o texto ]'
                    h1 = f'Visita liberada'
                    print(h1, txt)
                    return(h1, txt)                   
                    
                return(h1, txt)
            else:
                h1 =  'Dirija-se à recepção'
                txt = 'Usuário sem histórico de visitas.'
                print(h1, txt)
                return(h1, txt)
    else:
        h1 =  'Dirija-se à recepção'
        txt = 'Usuário não encontrado.'
        print(h1, txt)
        return(h1, txt)


