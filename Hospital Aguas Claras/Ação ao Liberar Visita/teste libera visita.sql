
USE W_Access

With Main as ( 
            Select 
            (select count(CHID) from CHActiveVisits where ContactCHID = 5546 and VisAuxLst01 = 0) as contact_active_visits 
            ,(select MaxVisitors from CfgCHTypesVisitsContacts where Chtype = 8 and CHTypeVisitor = 1 
                    and PartitionID = 2 ) as Max_visitor 
            ) 
            select * from Main


;With Main2 as ( 
            Select 
            (select count(CHID) from CHActiveVisits where ContactCHID = 5546 and VisAuxLst01 = 1) as contact_active_visits 
            ,(select MaxVisitors from CfgCHTypesVisitsContacts where Chtype = 8 and CHTypeVisitor = 1 
                    and PartitionID = 4 ) as Max_visitor 
            ) 
            select * from Main2


