Select FirstName, chmain.chid, CHAux.AuxLst02, combo_unid.strLanguage2 from chmain 
Inner join chaux on chmain.chid= chaux.chid
LEFT JOIN W_Access..CfgCHComboFields combo_unid ON CHAux.AuxLst02= combo_unid.ComboIndex AND combo_unid.FieldID = 'lstBDA_AuxLst02' AND combo_unid.CHType = CHMain.CHType
Where chmain.CHType = 2
