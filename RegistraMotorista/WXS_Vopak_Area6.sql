USE [W_Access_Events]
GO

/****** Object:  View [dbo].[WXS_Vopak_Area6]    Script Date: 12/6/2021 8:52:26 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


ALTER VIEW [dbo].[WXS_Vopak_Area6] AS

WITH Main AS (

SELECT 
Row_number() OVER (partition BY CHMain.CHID ORDER BY events.eventdatetime DESC) RN,
events.eventdatetime as 'EventDateTime',
SourceID as ReaderID,
CHMain.CHID,
AuxText03 as IdCorporate,
chmain.FirstName, 
CASE 
	WHEN chmain.CHID = chid_link.CHID THEN chid_link.LinkedCHID
	WHEN chmain.CHID = lk_chid.LinkedCHID THEN lk_chid.CHID
END as LinkedCHID, 
CASE 
	WHEN chmain.CHID = chid_link.CHID THEN (Select FirstName from W_Access..CHMain where CHID = chid_link.LinkedCHID)
	WHEN chmain.CHID = lk_chid.LinkedCHID THEN (Select FirstName from W_Access..CHMain where CHID = lk_chid.CHID)
END as ExpectedPlate,
Name as 'LogArea6',
Value
from W_Access..CHMain
left Join Events on Events.CHID = CHMain.CHID
JOIN W_Access..CHAux ON CHAux.CHID = CHMain.CHID
LEFT JOIN EventsProperties ep on ep.EventID = Events.EventID
left join W_Access..CHLinkedCHs chid_link on chid_link.CHID = CHMain.CHID
left join W_Access..CHLinkedCHs lk_chid on lk_chid.LinkedCHID = CHMain.CHID
where Events.CHType = 2
and EventHWID in (71, 73, 75)
)

SELECT 
EventDateTime, 
ReaderID,
CHID, 
IdCorporate,
FirstName, 
LinkedCHID, 
ExpectedPlate, 
LogArea6, 
Value 
FROM Main
WHERE rn = 1
and EventDateTime > DATEADD(DAY, -1, EventDateTime)

GO


