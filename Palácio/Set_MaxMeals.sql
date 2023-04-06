USE W_Access
UPDATE CHMain
SET MaxMeals = 1, CHDownloadRequired = 1
FROM CHMain
INNER JOIN CHCards ON CHMain.CHID = CHCards.CHID
WHERE CardState = 0 AND CHType = 2 AND CHState = 0 AND CHMain.CHID IN (SELECT CHID FROM CHGroups)





