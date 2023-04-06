import requests, json, traceback, sys, base64


try:

    def createUser(*args):
        print('Create User')
        print(args[0])
    #def createUser(FirstName, IDNumber):    
        if args[0]['IdNumber']:    
            IdNumber = args[0]['IdNumber']         
        else:
            print('Sem IdNumber')
            sys.exit(1)
        

        if args[0]['FirstName']:    
            FirstName = args[0]['FirstName']         
        else:
            sys.exit(1)

        #if args[0]['CHType']:    
            #CHType = args[0]['CHType']         
        #else:
            #sys.exit(1)


        #url = "http://192.168.1.106:80/W-AccessAPI/v1/"
        url = "http://localhost/W-AccessAPI/v1/"

        h = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180' }

        print("\n* Cardholders - Get by IdNumber")
        cardholder = None
        reply = requests.get(url + 'cardholders', headers=h, params = (("IdNumber", IdNumber),))
        reply_json = reply.json()
        if reply.status_code == requests.codes.ok:
            print("Found Cardholder: Name=%s"%(reply_json["FirstName"]))
            cardholder = reply_json
        elif reply.status_code == requests.codes.not_found:
            print("Cardholder not found")
        else:
            print("Error: " + reply_json["Message"])


        if not cardholder:
            print("\n* Cardholders - Create")
            print(FirstName)
            new_cardholder = { "FirstName": FirstName, "CHType": CHType, "IdNumber": IdNumber, "PartitionID": 1}
            reply = requests.post(url + 'cardholders', json=new_cardholder, headers=h)
            reply_json = reply.json()
            if reply.status_code == requests.codes.created:
                print("New CHID: %d"%(reply_json["CHID"]))
                cardholder = reply_json
            else:
                print("Error: " + reply_json["Message"])
                if "ModelState" in reply_json.keys():
                    for field_name in reply_json["ModelState"].keys():
                        print("%s: %s"%(field_name, ";".join(reply_json["ModelState"][field_name])))

        if not cardholder:
            sys.exit(1)

        print("\n* Cardholders - Update")

        cardholder["FirstName"] = FirstName
        cardholder["IDNumber"] = IdNumber
        cardholder["CHType"] = CHType

        ch = args[0]

        if 'CardNumber' in ch.keys():
            CardNumber = args[0]['CardNumber']
        else:
            CardNumber = IdNumber[:6]
        
        if 'EMail' in ch.keys():
            cardholder["EMail"] = args[0]['EMail']
        if 'AuxText01' in ch.keys():
            cardholder["AuxText01"] = args[0]['AuxText01'][:50]
        if 'AuxText02' in ch.keys():
            cardholder["AuxText02"] = args[0]['AuxText02'][:50]
        if 'AuxText03' in ch.keys():
            cardholder["AuxText03"] = args[0]['AuxText03'][:50]      
        if 'AuxText04' in ch.keys():
            cardholder["AuxText04"] = args[0]['AuxText04'][:50]
        if 'AuxText05' in ch.keys():
            cardholder["AuxText05"] = args[0]['AuxText05'][:50]
        if 'AuxText06' in ch.keys():
            cardholder["AuxText06"] = args[0]['AuxText06'][:50]
        if 'AuxText07' in ch.keys():
            cardholder["AuxText07"] = args[0]['AuxText07'][:50]        
        if 'AuxText08' in ch.keys():
            cardholder["AuxText08"] = args[0]['AuxText08'][:50]
        if 'AuxText09' in ch.keys():
            cardholder["AuxText09"] = args[0]['AuxText09'][:50]
        if 'AuxText10' in ch.keys():
            cardholder["AuxText10"] = args[0]['AuxText10'][:50]
        if 'AuxText11' in ch.keys():
            cardholder["AuxText11"] = args[0]['AuxText11'][:50]     
        if 'AuxText12' in ch.keys():
            cardholder["AuxText12"] = args[0]['AuxText12'][:50]
        if 'AuxText13' in ch.keys():
            cardholder["AuxText13"] = args[0]['AuxText13'][:50]
        if 'AuxText14' in ch.keys():
            cardholder["AuxText14"] = args[0]['AuxText14'][:50]
        if 'AuxText15' in ch.keys():
            cardholder["AuxText15"] = args[0]['AuxText15'][:50]      

        reply = requests.put(url + 'cardholders', json=cardholder, headers=h)
        if reply.status_code == requests.codes.no_content:
            print("Cardholder update OK")
        else:
            print("Error: " + reply.json()["Message"])
            

        print("\n* Card - Get by ClearCode")
        card = None
        Import_ClearCode = str(CardNumber)
        reply = requests.get(url + 'cards', headers=h, params = (("ClearCode", Import_ClearCode),))
        reply_json = reply.json()
        if reply.status_code == requests.codes.ok:
            print("\n* Found Card: %s %s"%(reply_json["CardID"], reply_json["CardEndValidityDateTime"]))
            card = reply_json
        elif reply.status_code == requests.codes.not_found:
            print("Card not found")
        else:
            print("Error: " + reply_json["Message"])


        if card and card["CHID"]:
            print("\n* Card is assigned. Unassigning it")
            reply = requests.delete(url + 'cardholders/%d/cards/%d'%(card["CHID"], card["CardID"]), json=card, headers=h)
            if reply.status_code == requests.codes.no_content:
                print("Card unassigned")
            elif reply.status_code == requests.codes.not_found:
                print("Card not found for unassign")
            else:
                print("Error: " + reply.json()["Message"])


        if card:
            print("\n* Card - Delete")
            reply = requests.delete(url + 'cards', headers=h, params = (("ClearCode", Import_ClearCode),))
            if reply.status_code == requests.codes.no_content:
                print("Card Deleted")
            elif reply.status_code == requests.codes.not_found:
                print("Card not found for deletion")
            else:
                reply_json = reply.json()
                print("Error: " + reply.json()["Message"])
            card = None


        if not card:
            print("\n* Card - Create resident card (CardType = 0)")
            new_card = { "ClearCode": Import_ClearCode, "CardNumber": CardNumber, "PartitionID": 0, "CardType" : 0 }
            reply = requests.post(url + 'cards', json=new_card, headers=h)
            reply_json = reply.json()
            if reply.status_code == requests.codes.created:
                card = reply_json
                print("New CardID: %d"%(card["CardID"]))
            else:
                print("Error: " + reply_json["Message"])


        if card:
            print("\n* Card - Assign to Cardholder")
            #card["CardEndValidityDateTime"] = "2016-01-01T10:00:00"
            reply = requests.post(url + 'cardholders/%d/cards'%(cardholder["CHID"]), json=card, headers=h)
            reply_json = reply.json()
            if reply.status_code == requests.codes.created:
                card = reply_json
                print("Card assigned")
                print("%s %s"%(card["CardID"], card["CardEndValidityDateTime"]))
            else:
                print("Error: " + reply_json["Message"])


        # AccessLevels - Get All Access Levels
        reply = requests.get(url + 'accessLevels', headers=h, params=(("fields", "AccessLevelID,AccessLevelName"),))
        reply_json = reply.json()
        if reply.status_code == requests.codes.ok:
            print("\n* AccessLevels:")
            for access_level in reply_json:
                print("ID=%d, Name=%s"%(access_level["AccessLevelID"], access_level["AccessLevelName"]))
        else:
            print("Error: " + reply_json["Message"])


        print("\n* CHAccessLevels - List Cardholder's AccessLevels IDs")
        ch_access_levels = []
        reply = requests.get(url + 'cardholders/%d/accessLevels'%(cardholder["CHID"]), headers=h)
        reply_json = reply.json()
        if reply.status_code == requests.codes.ok:
            ch_access_levels = reply_json
            print("Current AccessLevels IDs Assigned to %s:"%(cardholder["FirstName"]))
            for ch_access_level in ch_access_levels:
                print("ID=%d"%(ch_access_level["AccessLevelID"]))
        else:
            print("Error: " + reply_json["Message"])


        print("\n* CHAccessLevels - Unassign all AccessLevels from Cardholder")
        for ch_access_level in ch_access_levels:
            reply = requests.delete(url + 'cardholders/%d/accessLevels/%d'%(cardholder["CHID"], ch_access_level["AccessLevelID"]), headers=h)
            if reply.status_code == requests.codes.no_content:
                print("Unassigned AccessLevelsID %d from %s:"%(ch_access_level["AccessLevelID"],cardholder["FirstName"]))
            else:
                print("Error: " + reply.json()["Message"])


        print("\n* AccessLevels - Get Access Level by Name")
        access_level = None
        reply = requests.get(url + 'accessLevels', headers=h, params=(("AccessLevelName", "Total"),))
        if reply.status_code == requests.codes.ok:
            access_level = reply.json()
            print("AccessLevel 'Total' Found: ID=%d, Name=%s"%(access_level["AccessLevelID"], access_level["AccessLevelName"]))
        elif reply.status_code == requests.codes.not_found:
            print("Access Level 'Total' not found")
        else:
            print("Error: " + reply.json()["Message"])

        if not access_level:
            print("\n* AccessLevel - Create AccessLevel 'Total'")
            new_access_level = { "AccessLevelName": "Total", "LocalityID": 1, "PartitionID": 0 }
            reply = requests.post(url + 'accessLevels', json=new_access_level, headers=h)
            reply_json = reply.json()
            if reply.status_code == requests.codes.created:
                access_level = reply_json
                print("New AccessLevelID: %d"%(access_level["AccessLevelID"]))
            else:
                print("Error: " + reply_json["Message"])

        if access_level:
            print("\n* CHAccessLevels - Assign AccessLevel 'Total' to CH")
            reply = requests.post(url + 'cardholders/%d/accesslevels/%d'%(cardholder["CHID"],access_level["AccessLevelID"]), headers=h)
            reply_json = reply.json()
            if reply.status_code == requests.codes.created:
                ch_access_level = reply_json
                print("Access Level 'Total' assigned")
                print("CHID=%d AccessLevelID=%d"%(ch_access_level["CHID"], ch_access_level["AccessLevelID"]))
            else:
                print("Error: " + reply_json["Message"])


        print("\n* Events - Show events since a given date (up to 50)")
        reply = requests.get(url + 'events', headers=h, params=(("offset", 0), ("limit", 50), ("minEventDateTime", "2015-01-01T00:00:00"), ("fields", "EventDateTime,EventType,EventHWID,SourceName,SourceValue")))
        if reply.status_code == requests.codes.ok:
            events = reply.json()
            print("Events:")
            for event in events:
                print("%s %s %s %s %s"%(event["EventDateTime"], event["EventType"], event["EventHWID"], event["SourceName"], event["SourceValue"]))
        else:
            print("Error: " + reply.json()["Message"])




except Exception as ex:
    print(ex)
    traceback.print_exc(file=sys.stdout)

#sys.stdin.readline()

# Cardholder model reference
##    {
##      "CHID": 0,
##      "CHType": 0,
##      "FirstName": "",
##      "LastName": "",
##      "CompanyID": 0,
##      "VisitorCompany": "",
##      "EMail": "",
##      "CHState": 0,
##      "IsUndesirable": False,
##      "IsUndesirableReason1": "",
##      "IsUndesirableReason2": "",
##      "PartitionID": 0,
##      "LastModifOnLocality": 0,
##      "LastModifDateTime": "",
##      "LastModifBy": "",
##      "CHStartValidityDateTime": "",
##      "CHEndValidityDateTime": "",
##      "CHDownloadRequired": False,
##      "TraceCH": False,
##      "Trace_AlmP": 0,
##      "Trace_Act": 0,
##      "TrustedLogin": "",
##      "DefFrontCardLayout": 0,
##      "DefBackCardLayout": 0,
##      "IdNumber": "",
##      "MaxTransits": 0,
##      "MaxMeals": 0,
##      "IgnoreTransitsCount": False,
##      "IgnoreMealsCount": False,
##      "IgnoreAntiPassback": False,
##      "IgnoreZoneCount": False,
##      "PIN": "",
##      "RequiresEscort": False,
##      "CanEscort": False,
##      "CanReceiveVisits": False,
##      "SubZoneID": 0,
##      "IgnoreRandomInspection": False,
##      "CHFloor": "",
##      "BdccState": 0,
##      "BdccIgnore": False,
##      "BdccCompanies": "",
##      "IdNumberType": 0,
##      "AuxText01": "",
##      "AuxText02": "",
##      "AuxText03": "",
##      "AuxText04": "",
##      "AuxText05": "",
##      "AuxText06": "",
##      "AuxText07": "",
##      "AuxText08": "",
##      "AuxText09": "",
##      "AuxText10": "",
##      "AuxText11": "",
##      "AuxText12": "",
##      "AuxText13": "",
##      "AuxText14": "",
##      "AuxText15": "",
##      "AuxTextA01": "",
##      "AuxTextA02": "",
##      "AuxTextA03": "",
##      "AuxTextA04": "",
##      "AuxTextA05": "",
##      "AuxLst01": 0,
##      "AuxLst02": 0,
##      "AuxLst03": 0,
##      "AuxLst04": 0,
##      "AuxLst05": 0,
##      "AuxLst06": 0,
##      "AuxLst07": 0,
##      "AuxLst08": 0,
##      "AuxLst09": 0,
##      "AuxLst10": 0,
##      "AuxLst11": 0,
##      "AuxLst12": 0,
##      "AuxLst13": 0,
##      "AuxLst14": 0,
##      "AuxLst15": 0,
##      "AuxChk01": False,
##      "AuxChk02": False,
##      "AuxChk03": False,
##      "AuxChk04": False,
##      "AuxChk05": False,
##      "AuxChk06": False,
##      "AuxChk07": False,
##      "AuxChk08": False,
##      "AuxChk09": False,
##      "AuxChk10": False,
##      "AuxDte01": "",
##      "AuxDte02": "",
##      "AuxDte03": "",
##      "AuxDte04": "",
##      "AuxDte05": "",
##      "AuxDte06": "",
##      "AuxDte07": "",
##      "AuxDte08": "",
##      "AuxDte09": "",
##      "AuxDte10": ""
##    }

