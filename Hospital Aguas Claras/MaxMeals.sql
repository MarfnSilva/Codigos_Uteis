USE W_Access
UPDATE CHMain
SET MaxMeals = 1
FROM CHMain
JOIN CHCards ON CHMain.CHID = CHCards.CHID
WHERE CardState = 0 AND CHType = 2 AND CHState = 0
OR
CHType = 5 AND CompanyID IN (SELECT CompanyID FROM CHCompanies WHERE CompanyAuxChk01 = 1 OR CompanyAuxChk02 = 1)

DELETE CHAccessLevels
WHERE AccessLevelID IN (170, 659)

INSERT INTO CHAccessLevels(CHID, AccessLevelID)
SELECT CHMain.CHID, 170 
FROM CHMain
JOIN CHCards ON CHMain.CHID = CHCards.CHID
WHERE CHCards.CHID IS NOT NULL AND CardState = 0 AND CHType = 2 AND CHState = 0 AND CHMain.PartitionID = 5
OR
CHType = 5 AND CompanyID IN (SELECT CompanyID FROM CHCompanies WHERE CompanyAuxChk01 = 1)

INSERT INTO CHAccessLevels(CHID, AccessLevelID)
SELECT CHMain.CHID, 659 
FROM CHMain
JOIN CHCards ON CHMain.CHID = CHCards.CHID
WHERE CHCards.CHID IS NOT NULL AND CardState = 0 AND CHType = 2 AND CHState = 0 AND CHMain.PartitionID = 7
OR
CHType = 5 AND CompanyID IN (SELECT CompanyID FROM CHCompanies WHERE CompanyAuxChk02 = 1)

UPDATE CHMain
SET CHDownloadRequired = 1
FROM CHMain INNER JOIN CHAccessLevels ON CHMain.CHID = CHAccessLevels.CHID
WHERE AccessLevelID IN (170, 659)