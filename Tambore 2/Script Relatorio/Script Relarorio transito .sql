DECLARE

@CHID int = 3359

Select 
		Events.CHID,
		Events.Firstname,
		CHMain.IdNumber AS DOCUMENTO,
		CfgHWEvents.strLanguage2 AS Evento,
		Events.GMTOffset,
		CfgCHTypes.strLanguage2 AS CHType,
		Events.SourceName AS Leitora,
		Events.EventDateTIme AS EventDateTime,
		VisitHistory.ContactCHID,
		VisitHistory.ContactFirstName AS Contato_Visitado,
		contact.AuxLst02 AS Quadra,
		combo_unid.StrLanguage2	AS N_Quadra,
		contact.AuxLst01 AS Alameda,
		combo_Alameda.StrLanguage2	AS N_Alamenda,
		contact.AuxText04 AS Numero,
		VisAuxTextA01 AS OBS
		
From Events 
JOIN W_Access..CHMain ON CHMain.CHID = Events.CHID 
JOIN W_Access..CHAux on CHMain.CHID = CHAux.CHID
JOIN W_Access..CfgCHTypes ON CfgCHTypes.CHType = Events.CHType
JOIN W_Access..CfgHWEvents ON CfgHWEvents.EventHWID = Events.EventHWID
LEFT JOIN VisitHistory ON (Events.CHID = VisitHistory.CHID AND EventDateTime between VisitStart AND VisitEnd)
LEFT JOIN W_Access..CHAux contact ON contact.chid = VisitHistory.ContactCHID
LEFT JOIN W_Access..CHMain contact_chmain on VisitHistory.ContactCHID = contact_chmain.chid
LEFT JOIN W_Access..CfgCHComboFields combo_unid ON contact.AuxLst02= combo_unid.ComboIndex AND combo_unid.FieldID = 'lstBDA_AuxLst02' AND combo_unid.CHType = contact_chmain.CHType
LEFT JOIN W_Access..CfgCHComboFields combo_Alameda ON  contact.AuxLst01 = combo_Alameda.ComboIndex AND combo_Alameda.FieldID= 'lstBDA_AuxLst01' AND  combo_Alameda.CHType =  contact_chmain.CHType
WHERE W_ACCESS_Events..Events.EventType = 1
	AND CHMain.CHType in (1, 6)
	AND Events.EventHWID <> 150
	AND Events.EventHWID in (71, 73, 75)
	--AND VisitHistory.ContactCHID is not null  order by ContactCHID desc
	--AND Events.EventDateTime BETWEEN @_lblBD_StartTime_StartDate AND @_lblBD_EndTime_EndDate
	




--Select * from Events
--Where chid = 3359  and EventHWID =71 

--Select * from VisitHistory
--Where chid = 328
