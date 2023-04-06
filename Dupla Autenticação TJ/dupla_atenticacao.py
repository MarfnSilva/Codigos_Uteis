# -*- coding: utf-8 -*-

import os, wmi, win32serviceutil, pyodbc, time, sys 
from functions import *

service = 'WXSVirtualControllers'# Serviço do Gerenciador
task = f'WXS_SiteController_{id_gerenciador()}.exe'

# Encerra a Tarefa do gerenciador
os.system(f"taskkill /im {task} /T /F")
time.sleep(0.2)

# Exclui o Arquivo database.db da pasta do gerenciador
diretorio = f"C:\Program Files (x86)\W-Access Server\Services\SiteControllers\Virtual SiteControllers\SiteController_{id_gerenciador()}\data\database.db"
if os.path.exists(diretorio):
    os.remove(diretorio)

# Percorre cada leitora configurada no arquivo Settings.json
for id in settings["leitoras"]:
    if id["id_leitora"] != 0 : 

        # Atualiza o FaceMultiFactorForEntry para 1, para ativar a DA na leitora
        if options().upper() == "ATIVAR":
            leitora = id["id_leitora"]
            conn = pyodbc.connect('Driver='+odbcdriver()+';Server='+servername()+'\WACCESS;Database='+databasename()+';Trusted_Connection=yes')  
            cursor = conn.cursor()
            script = f"update CfgHWReaders set FaceMultiFactorForEntry = 1 where ReaderID = {leitora}"
            cursor.execute(script)
            cursor.commit()
            time.sleep(0.2)

        # Atualiza o FaceMultiFactorForEntry para 0, para desativar a DA na leitora
        elif options().upper() == "DESATIVAR":
            leitora = id["id_leitora"]
            conn = pyodbc.connect('Driver='+odbcdriver()+';Server='+servername()+'\WACCESS;Database='+databasename()+';Trusted_Connection=yes')  
            cursor = conn.cursor()
            script = f"update CfgHWReaders set FaceMultiFactorForEntry = 0 where ReaderID = {leitora}"
            cursor.execute(script)
            cursor.commit()
            time.sleep(0.2)

        else:
            print("Campo 'Options' Inválido! ")
    else:
        continue

# Reinicia o Serviço do Gerenciador para aplicar a alteração
win32serviceutil.RestartService(service)
time.sleep(0.2)
input(f"Processo finalizado. Pressione qualquer tecla para sair")
sys.exit(0)
