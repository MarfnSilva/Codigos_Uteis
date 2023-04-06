# -*- coding: utf-8 -*-

import urllib
import urllib.request
# from urllib.request import urlopen
# from pprint import pprint

site=str("localhost/W-Access")
try:
    site1=urllib.request.urlopen('https://'+site+'/')
    
except urllib.request.URLError as exec:
    print(f'O Site não está acessível no momento - {exec.reason}')
    #print(f'{exec}')
else:
    print(f'HTTPResponse: {site1.reason}!')
    #print(site1.reason)
    


# with urlopen("https://www.google.com") as response:
#     pprint(dir(response	))
#   body = response.read()

# print(body[:15])