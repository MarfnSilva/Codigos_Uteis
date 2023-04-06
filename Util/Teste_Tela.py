# -*- coding: utf-8 # -*- 

from matplotlib.font_manager import json_dump
from GenericTrace import report_exception, trace
import requests, json, sys
from datetime import datetime, timedelta   


waccess_api_server = 'localhost'
waccess_utc_offset = '-180'
waccessapi_endpoint = 'http://localhost/W-AccessAPI/v1/'
waccessapi_header = { 'WAccessAuthentication': 'WAccessAPI:#WAccessAPI#', 'WAccessUtcOffset': '-180'}

user_chid = 8119#sys.argv[1]
user_chtype = 7#sys.argv[2]
# user = json.loads(sys.argv[1])


# user = sys.argv[1]#str(sys.argv[1]).replace("null", "None").replace("false", "False").replace("true", "True")
# wxs_user = {"cardholder_json":{"CHAux":[{"CHID":8119,"AuxText01":None,"AuxText02":None,"AuxText03":None,"AuxText04":None,"AuxText05":None,"AuxText06":None,"AuxText07":None,"AuxText08":None,"AuxText09":None,"AuxText10":None,"AuxText11":None,"AuxText12":None,"AuxText13":None,"AuxText14":None,"AuxText15":None,"AuxTextA01":None,"AuxTextA02":None,"AuxTextA03":None,"AuxTextA04":None,"AuxTextA05":None,"AuxLst01":None,"AuxLst02":None,"AuxLst03":None,"AuxLst04":None,"AuxLst05":None,"AuxLst06":None,"AuxLst07":None,"AuxLst08":None,"AuxLst09":None,"AuxLst10":None,"AuxLst11":None,"AuxLst12":None,"AuxLst13":None,"AuxLst14":None,"AuxLst15":None,"AuxChk01":False,"AuxChk02":False,"AuxChk03":False,"AuxChk04":False,"AuxChk05":False,"AuxChk06":False,"AuxChk07":False,"AuxChk08":False,"AuxChk09":False,"AuxChk10":False,"AuxDte01":None,"AuxDte02":None,"AuxDte03":None,"AuxDte04":None,"AuxDte05":None,"AuxDte06":None,"AuxDte07":None,"AuxDte08":None,"AuxDte09":None,"AuxDte10":None}],
# "CHAccessLevels":[],"CHMain":[{"CHID":8119,"CHType":7,"FirstName":"MURILO HELIO DE LIMA","LastName":None,"CompanyID":11,"VisitorCompany":None,"EMail":None,"CHState":0,"IsUndesirable":False,"IsUndesirableReason1":None,"IsUndesirableReason2":None,"PartitionID":1,"LastModifOnLocality":1,"LastModifDateTime":"2022-03-17T19:48:56.39","LastModifBy":None,"CHStartValidityDateTime":"2022-02-15T19:17:45.263","CHEndValidityDateTime":"2027-02-14T16:17:45","CHDownloadRequired":None,"TraceCH":None,"Trace_AlmP":1,"Trace_Act":None,"TrustedLogin":None,"DefFrontCardLayout":None,"DefBackCardLayout":None,"IdNumber":"16476225812","MaxTransits":None,"MaxMeals":None,"IgnoreTransitsCount":True,"IgnoreMealsCount":False,"IgnoreAntiPassback":False,"IgnoreZoneCount":False,"PIN":None,"RequiresEscort":False,"CanEscort":False,"CanReceiveVisits":True,"SubZoneID":None,"IgnoreRandomInspection":False,"CHFloor":None,"BdccState":0,"BdccIgnore":False,"BdccCompanies":None,"IdNumberType":None,"DisableAutoReturnTempCard":False,"DisableAutoReturnVisCard":False}],"CHLastTransit":[],"CHCards":[{"CardID":8065,"ClearCode":"F_000008119","CardNumber":8119,"FacilityCode":0,"CardType":0,"CHID":8119,"CardDownloadRequired":False,"CardState":0,"PartitionID":24,"CardStartValidityDateTime":"2022-02-15T19:17:45.263","CardEndValidityDateTime":"2027-02-14T16:17:45","TempCardLink":0,"OriginalCardState":0,"IPRdrUserID":8062,"IPRdrAlwaysEnabled":False,"IsAutomaticCard":True}],"CHFingerprints":[{"CHID":8119,"Finger0":None,"Finger0Duress":False,"FingerImgStr0":None,"Finger1":None,"Finger1Duress":False,"FingerImgStr1":None,"Finger2":None,"Finger2Duress":False,"FingerImgStr2":None,"Finger3":None,"Finger3Duress":False,"FingerImgStr3":None,"Finger4":None,"Finger4Duress":False,"FingerImgStr4":None,"Finger5":None,"Finger5Duress":False,"FingerImgStr5":None,"Finger6":None,"Finger6Duress":False,"FingerImgStr6":None,"Finger7":None,"Finger7Duress":False,"FingerImgStr7":None,"Finger8":None,"Finger8Duress":False,"FingerImgStr8":None,"Finger9":None,"Finger9Duress":False,"FingerImgStr9":None,"Privilege":0,"UserGroup":1,"ChangePwdNextAccess":False}]},"visit_json":None}
#user = '{"cardholder_json":{"CHAux":[{"CHID":8119,"AuxText01":null,"AuxText02":null,"AuxText03":null,"AuxText04":null,"AuxText05":null,"AuxText06":null,"AuxText07":null,"AuxText08":null,"AuxText09":null,"AuxText10":null,"AuxText11":null,"AuxText12":null,"AuxText13":null,"AuxText14":null,"AuxText15":null,"AuxTextA01":null,"AuxTextA02":null,"AuxTextA03":null,"AuxTextA04":null,"AuxTextA05":null,"AuxLst01":null,"AuxLst02":null,"AuxLst03":null,"AuxLst04":null,"AuxLst05":null,"AuxLst06":null,"AuxLst07":null,"AuxLst08":null,"AuxLst09":null,"AuxLst10":null,"AuxLst11":null,"AuxLst12":null,"AuxLst13":null,"AuxLst14":null,"AuxLst15":null,"AuxChk01":false,"AuxChk02":false,"AuxChk03":false,"AuxChk04":false,"AuxChk05":false,"AuxChk06":false,"AuxChk07":false,"AuxChk08":false,"AuxChk09":false,"AuxChk10":false,"AuxDte01":null,"AuxDte02":null,"AuxDte03":null,"AuxDte04":null,"AuxDte05":null,"AuxDte06":null,"AuxDte07":null,"AuxDte08":null,"AuxDte09":null,"AuxDte10":null}],"CHAccessLevels":[],"CHMain":[{"CHID":8119,"CHType":7,"FirstName":"MURILO HELIO DE LIMA","LastName":null,"CompanyID":11,"VisitorCompany":null,"EMail":null,"CHState":0,"IsUndesirable":false,"IsUndesirableReason1":null,"IsUndesirableReason2":null,"PartitionID":1,"LastModifOnLocality":1,"LastModifDateTime":"2022-03-17T19:48:56.39","LastModifBy":null,"CHStartValidityDateTime":"2022-02-15T19:17:45.263","CHEndValidityDateTime":"2027-02-14T16:17:45","CHDownloadRequired":null,"TraceCH":null,"Trace_AlmP":1,"Trace_Act":null,"TrustedLogin":null,"DefFrontCardLayout":null,"DefBackCardLayout":null,"IdNumber":"16476225812","MaxTransits":null,"MaxMeals":null,"IgnoreTransitsCount":true,"IgnoreMealsCount":false,"IgnoreAntiPassback":false,"IgnoreZoneCount":false,"PIN":null,"RequiresEscort":false,"CanEscort":false,"CanReceiveVisits":true,"SubZoneID":null,"IgnoreRandomInspection":false,"CHFloor":null,"BdccState":0,"BdccIgnore":false,"BdccCompanies":null,"IdNumberType":null,"DisableAutoReturnTempCard":false,"DisableAutoReturnVisCard":false}],"CHLastTransit":[],"CHCards":[{"CardID":8065,"ClearCode":"F_000008119","CardNumber":8119,"FacilityCode":0,"CardType":0,"CHID":8119,"CardDownloadRequired":false,"CardState":0,"PartitionID":24,"CardStartValidityDateTime":"2022-02-15T19:17:45.263","CardEndValidityDateTime":"2027-02-14T16:17:45","TempCardLink":0,"OriginalCardState":0,"IPRdrUserID":8062,"IPRdrAlwaysEnabled":false,"IsAutomaticCard":true}],"CHFingerprints":[{"CHID":8119,"Finger0":null,"Finger0Duress":false,"FingerImgStr0":null,"Finger1":null,"Finger1Duress":false,"FingerImgStr1":null,"Finger2":null,"Finger2Duress":false,"FingerImgStr2":null,"Finger3":null,"Finger3Duress":false,"FingerImgStr3":null,"Finger4":null,"Finger4Duress":false,"FingerImgStr4":null,"Finger5":null,"Finger5Duress":false,"FingerImgStr5":null,"Finger6":null,"Finger6Duress":false,"FingerImgStr6":null,"Finger7":null,"Finger7Duress":false,"FingerImgStr7":null,"Finger8":null,"Finger8Duress":false,"FingerImgStr8":null,"Finger9":null,"Finger9Duress":false,"FingerImgStr9":null,"Privilege":0,"UserGroup":1,"ChangePwdNextAccess":false}]},"visit_json":null}'
end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")

get_user1 = requests.get(waccessapi_endpoint + f'cardholders/' + str(user_chid), headers=waccessapi_header, params=(("CHType", user_chtype),("limit", '20000')))
get_user_json = get_user1.json()

get_user_json["FirstName"] = "Teste - OK"
# user = {"FirstName" : "Teste - OK","CHID" : 8129, "CHEndValidityDateTime" : end_validity_str}
#wxs_user = json.loads(user)
# print('-----------------------------------------------')
# print(wxs_user["cardholder_json"]['CHMain'])
# for user in wxs_user["cardholder_json"]['CHMain']:
#     print(user['FirstName'])
requests.put(waccessapi_endpoint + f'cardholders', json=get_user_json, headers=waccessapi_header, params=(("callAction", False),))

sys.exit(0)


