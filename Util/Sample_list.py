
# -*- coding: utf-8 -*-



wxs_user ={
    "grupos": 
    [
    {"texto1" : 1,
    "id" : 2,
    "texto3" : 3}, 
    {"texto1" : 5,
    "id" : 6,
    "texto3" : 7}
    ]
   
}



lista = []
for teste in wxs_user["grupos"]:
    lista.append(teste["id"])

print(lista)