USE W_Access_Events
DELETE FROM EventPictures
WHERE EventPictureID IN (
SELECT 
EventPictureID
FROM EventPictures
JOIN Events ON Events.EventID = EventPictures.EventID
WHERE EventDateTime <= DATEADD(DAY, -30, GETDATE())
)