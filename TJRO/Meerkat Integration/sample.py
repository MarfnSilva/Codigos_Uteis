# -*- coding: utf-8 -*-

from meerkat_helpers import *
from GenericTrace import *
import sys, threading



last_modify = (datetime.now() - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
get_user = requests_get('cardholders', params=(("CHType", 2),("CHType", 3),("CHType", 7),("CHType", 8),("lastModifDateTimeStart", last_modify),
                                                ("fields", "CHID,Firstname,CHType,CHState,Cards"),("includeTables", "Cards")))
count_get = get_user.json()

print(len(count_get))