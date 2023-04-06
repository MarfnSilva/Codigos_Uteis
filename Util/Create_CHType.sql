DECLARE @CopyFromCHType int = 8
DECLARE @NewCHType int = (SELECT MAX(CHType) + 1 FROM CfgCHTypes)
DECLARE @strLanguage1 varchar(50) = 'Truck'
DECLARE @strLanguage2 varchar(50) = 'Caminhão'
DECLARE @strLanguage3 varchar(50) = 'Camión'
DECLARE @strLanguage4 varchar(50) = ''

SELECT 'New CHType ' + CONVERT(varchar(50), @NewCHType)

INSERT INTO CfgCHTypes
SELECT
@NewCHType
,CHCategory
,@strLanguage1
,@strLanguage2
,@strLanguage3
,@strLanguage4
,CanReceiveVisits
,CanHaveAssets
,CanHaveVehicles
,CanHaveEquipments
,UniqueIdNumber
,CHTypeBdccIgnore
,AllowAutomaticCards
,DeleteAutomaticCards
,AutomaticCardPartitionID
,CHTypeEnabled
,TempCardDefaultValidityInHours
,TempCardDefaultValidityInHours
,DefaultValidityPeriodForVisitorsInMinutes
,VisitDefaultValidityTime
,MaxTemporaryCards
,DisableAutoReturnTempCard
,DisableAutoReturnVisCard
FROM CfgCHTypes WHERE CHType = @CopyFromCHType

INSERT INTO CfgCHComboFields
SELECT
FieldID
,@NewCHType
,ComboIndex
,CHCategory
,strLanguage1
,strLanguage2
,strLanguage3
,strLanguage4
FROM CfgCHComboFields
WHERE CHType = @CopyFromCHType

INSERT INTO CfgCHCustomPageControls
SELECT
ControlID
,@NewCHType
,Page
,StyleTop
,StyleLeft
,Height
,Width
,CssClass
,Visible
,TabIndex
,Capitalization
,ValidationExpression
,FieldMask
FROM CfgCHCustomPageControls
WHERE CHType = @CopyFromCHType

INSERT INTO CfgCHLinkedCHTypes
SELECT
@NewCHType
,LinkedCHType
FROM CfgCHLinkedCHTypes
WHERE CHType = @CopyFromCHType

INSERT INTO CfgCHMoreInfoWindows
SELECT
@NewCHType
,Height
,Width
,PosTop
,PosLeft
FROM CfgCHMoreInfoWindows
WHERE CHType = @CopyFromCHType

INSERT INTO CfgCOFieldLabels
SELECT
FieldID
,@NewCHType
,CHCategory
,strLanguage1
,strLanguage2
,strLanguage3
,strLanguage4
FROM CfgCOFieldLabels
WHERE CHType = @CopyFromCHType

INSERT INTO CfgSYPermissionSets
SELECT
PermissionSetID
,@NewCHType
,PermissionID
FROM CfgSYPermissionSets
WHERE CHType = @CopyFromCHType