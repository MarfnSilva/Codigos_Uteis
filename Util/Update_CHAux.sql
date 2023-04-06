SELECT * from Import_Palacio_2

select Id, auxtext10,  info5, idnumber,  socsecno, auxtext01
from Import_Palacio_2
JOIN CHAUx on (Id like Auxtext10)
JOIN CHMAIN ON (CHAux.CHID = CHMain.CHID)


update chaux
set auxtext01 = socsecno
from Import_Palacio_2
JOIN CHAUx on (Id like Auxtext10)


update chmain
set idnumber = info5
from Import_Palacio_2
JOIN CHAUx on (Id like Auxtext10)
JOIN CHMAIN ON (CHAux.CHID = CHMain.CHID)

