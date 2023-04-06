
import datetime

data_nasc1 = '26/03/1938'
#data_nasc1 = '26/03/1938 00:00:00'
data_12 = datetime.datetime.strptime(data_nasc1, '%d/%m/%Y').strftime('%Y-%m-%d 00:00:00')
print(data_12)



#data_saida = data_nasc1[0:10].replace('/','-')
#print(f'{data_saida} 00:00:00')