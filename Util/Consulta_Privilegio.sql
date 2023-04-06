opção 1
select 
CHMain.FirstName, 
(select CfgCHComboFields.strLanguage2 from CfgCHComboFields where FieldID = 'lstBD_privilege' 
and  
CHFingerprints.Privilege = CfgCHComboFields.ComboIndex) as privilegio
from CHMain
join CHFingerprints on CHFingerprints.CHID = CHMain.CHID

--------------------------------------------------------------------------------------------------------------

opção 2
select 
CHMain.FirstName, 
(select CfgCHComboFields.strLanguage2 from CfgCHComboFields where FieldID = 'lstBD_privilege' 
and 
(select Privilege from CHFingerprints where chid = CHMain.chid) = CfgCHComboFields.ComboIndex) as privilegio
from CHMain

--------------------------------------------------------------------------------------------------------------

opção 3
USE W_Access
SELECT 
CHMain.FirstName AS Nome,
CHMain.IdNumber AS Documento, 
(SELECT CfgCHComboFields.strLanguage2 FROM CfgCHComboFields WHERE FieldID = 'lstBD_privilege' 
and  
CHFingerprints.Privilege = CfgCHComboFields.ComboIndex) AS Privilegio
FROM CHMain
join CHFingerprints ON CHFingerprints.CHID = CHMain.CHID
WHERE CHFingerprints.Privilege <> 0