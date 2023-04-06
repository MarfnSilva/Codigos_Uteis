# -*- coding: utf-8 # -*- 
from turtle import color
from GenericTrace import report_exception, trace
import requests,pyodbc
from datetime import datetime, timedelta   
from Functions import *
import time
import openpyxl, pathlib, shutil

def teste(arquivo):
    print(f'executa script - {arquivo}')



if __name__ == '__main__':

    end_validity_dte = datetime.now() + timedelta(days=1825) # 1825 Days = 5 Years
    end_validity_str = end_validity_dte.strftime("%Y-%m-%dT%H:%M:%S")
    date_file = datetime.now()
    date_file_str = date_file.strftime("%Y-%m-%d")

    accesslvl = requests.get(waccessapi_endpoint + f'accessLevels', headers=waccessapi_header)
    accesslvl_list = accesslvl.json()

    companie = requests.get(waccessapi_endpoint + f'companies', headers=waccessapi_header)
    companie_list = companie.json()

    while True:
        trace('#################### Inicio da Varredura ####################', color = "orange")
        for file in companie_list:
            diretorio = pathlib.Path(f'{diretorio}')
            arquivos = tuple(diretorio.glob(f'**/{file["CompanyName"]}.xlsx'))
            if arquivos:
                for arquivo in arquivos:
                    trace(f'------- Arquivo encontrado com nome: {file["CompanyName"]}.xls -------', color = "blue")
                    teste(arquivo)
            else:
                trace(f'------- Nenhum Arquivo Encontrado com o nome: {file["CompanyName"]}.xls -------', color = "gray")
                time.sleep(0.8)
        trace('#################### FIm da Varredura ####################', color = "gold")
        time.sleep(2) 
