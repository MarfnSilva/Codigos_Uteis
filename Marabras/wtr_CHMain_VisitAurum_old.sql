SET QUOTED_IDENTIFIER ON
GO
-- ===========================================================================
-- Author: Marcelo Silva
-- Create date: 11/08/2022
-- Description: Trigger used to set IgnoreRandomInspection to "1" of visitors
-- ===========================================================================
CREATE TRIGGER wtr_CHMain_VisitAurum
   ON CHMain
   WITH ENCRYPTION
   AFTER INSERT, UPDATE
AS
BEGIN
SET NOCOUNT ON;

DECLARE @CHID int
DECLARE @CHType int

DECLARE CHMain_VisitAurum_cursor CURSOR LOCAL STATIC FOR
SELECT CHID FROM inserted

OPEN CHMain_VisitAurum_cursor  

FETCH NEXT FROM CHMain_VisitAurum_cursor
INTO @CHID

WHILE @@FETCH_STATUS = 0

BEGIN

SET @CHType = (SELECT CHType FROM CHMain WHERE CHID = @CHID)

IF @CHType = 1
UPDATE CHMain
SET IgnoreRandomInspection = 1 
WHERE CHID = @CHID
AND IgnoreRandomInspection = 0

FETCH NEXT FROM CHMain_VisitAurum_cursor
INTO @CHID
END

DEALLOCATE CHMain_VisitAurum_cursor

END
GO