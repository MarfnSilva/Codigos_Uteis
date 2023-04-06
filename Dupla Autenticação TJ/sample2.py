import os
from functions import *

task = f'WXS_SiteController_{id_gerenciador()}.exe'

diretorio = f"C:\Program Files (x86)\W-Access Server\Services\SiteControllers\Virtual SiteControllers\SiteController_{id_gerenciador()}\data\database.db"

if os.path.exists(diretorio):
    print('tem o arquivo')
else:
    print('não tem o arquivo')