# -*- coding: utf-8 -*-
import csv  
import json  
from WAccessApiClient import createUser
import requests, traceback, sys, base64
import time


print('Try')

try:
    print('Entrou no try')
    # Define Header 
    with open('Importa_User.csv', encoding="utf-8-sig", newline='') as f:
        reader = csv.reader(f)
        row1 = next(reader)

        
    # Open the CSV  
    f = open( 'Importa_User.csv', 'r', encoding="utf-8-sig") 
    next(f) 

    reader = csv.DictReader( f, fieldnames = (row1))  
    # Parse the CSV into JSON  
    out = json.dumps( [ row for row in reader ] )  
    # Save the JSON  
    
    f = open( 'import_base.json', 'w')  
    f.write(out)  
    f.flush()
    
    # >> --------------------- Call create/update Users -------------------

    # read file
    with open('import_base.json', 'r', encoding="utf-8-sig") as myfile:
        data=myfile.read()
        


    # parse file
    obj = json.loads(data)


    # Teste função (*args)
    def func(*args):
        print('--------------------------')       

    
    print(len(obj))

    for x in range(len(obj)):
        print(obj[x])


        #createUser(obj[x])

    # ------- Processa cada uma das linhas ---------
    for i in range(len(obj)):
        createUser(obj[i])
        func(obj[i])
        print('For')

    print('teste import')

except Exception as ex:
    print(ex)
    traceback.print_exc(file=sys.stdout)

