# -*- coding: utf-8 -*-

import os, wmi, win32serviceutil, pyodbc, time, sys 
from functions import *

for id in settings["leitoras"]:
    if id["id_leitora"] != 0 : 

        # Atualiza o FaceMultiFactorForEntry para 1, para ativar a DA na leitora
        if options().upper() == "ATIVAR":
            leitora = id["id_leitora"]
            conn = pyodbc.connect('Driver='+odbcdriver()+';Server='+servername()+'\W_ACCESS;Database='+databasename()+';Trusted_Connection=yes') 
            cursor = conn.cursor()
            script_partition = f"update CfgHWReaders set FaceMultiFactorForEntry = 1 where ReaderID = {leitora}"
            cursor.execute(script_partition)
            cursor.commit()
            time.sleep(0.2)

        # Atualiza o FaceMultiFactorForEntry para 0, para desativar a DA na leitora
        elif options.upper() == "DESATIVAR":
            leitora = id["id_leitora"]
            conn = pyodbc.connect('Driver='+odbcdriver()+';Server='+servername()+'\W_ACCESS;Database='+databasename()+';Trusted_Connection=yes') 
            cursor = conn.cursor()
            script_partition = f"update CfgHWReaders set FaceMultiFactorForEntry = 0 where ReaderID = {leitora}"
            cursor.execute(script_partition)
            cursor.commit()
            time.sleep(0.2)

        else:
            print("Campo 'Options' Inválido! ")
    else:
        continue