# -*- coding: utf-8 # -*- 

import pathlib


teste = 'old'

diretorio = pathlib.Path('C:/Users/marcelo.silva/Desktop/Codigos_Uteis/Marabras')
arquivos = diretorio.glob(f'**/Sample_{teste}.xlsx')
if arquivos:
    for arquivo in arquivos:
        print(arquivo)