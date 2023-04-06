
/*Evento de cartão invalido 13 */
/*Evento de acesso autori 70 */


Select Eventid, EventDateTime, EventHWID, CHID, ClearCode, CardNumber, chtype, FirstName, IdNumber, SourceID, SourceName from Events
Where EventHWID in (13,70) and EventType= 1 and  SourceID = 8  and ServerDateTime > DATEADD(SECOND,-50,GETUTCDATE())


