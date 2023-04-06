# -*- coding: utf-8 -*-

from arrow import utcnow
import requests, json, time, os, sqlite3
from datetime import datetime, timedelta

global settings
settings = json.loads(open('settings.json').read())

def default_url():
    global settings
    return settings["api_uri"]

def default_headers():
    global settings
    h = {"WAccessAuthentication": f"{settings['api_user']}:{settings['api_password']}", "WAccessUtcOffset": "-180"}
    return h

def ch_states():
    global settings
    return settings["ch_states"]

def ch_types():
    global settings
    return settings["ch_types"]

def db_connection():
    database = 'usuarios_expirados.db'
    if os.path.isfile(database):
        conn = sqlite3.connect(database)
        return(conn)
    else:
        print('Não existe')
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE Main (CHID INTEGER UNIQUE NOT NULL, INFO TEXT);""")
        print('Tabela criada com sucesso.')
        sql = ("CREATE INDEX index_chid ON Main (CHID);")
        cursor.execute(sql)
        return(conn)

def insert_local_db(chid,lastModify):
    conn = db_connection()
    script = f""" INSERT INTO Main (CHID, INFO) values ({chid}, "{lastModify}") """
    cur = conn.cursor()
    cur.execute(script)
    conn.commit()
    conn.close()

def write_local_db(chid, lastModify):
    conn = db_connection()
    script = f""" UPDATE Main set INFO = '{lastModify}' where chid = {chid} """
    cur = conn.cursor()
    cur.execute(script)
    conn.commit()
    conn.close()

def delete_local_db():
    conn = db_connection()
    script = f""" DELETE FROM Main"""
    cur = conn.cursor()
    cur.execute(script)
    conn.commit()
    conn.close()

def read_local_db(chid):
    conn = db_connection()
    script = f""" SELECT * from Main where chid = {chid} """
    cur = conn.cursor()
    c = cur.execute(script)
    result = c.fetchall()
    if not result:
        #insert_local_db(chid)
        return(None)
        # for wxs_chid, accesslevels in result:
        #     print(wxs_chid, accesslevels)
        #     return(accesslevels)
    conn.commit()
    conn.close()
    return(result)


start_time = True

while True:

    last_modify = (datetime.utcnow() - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
    
    if start_time == True:
        start = datetime.now()

    # for chtype in ch_types():
    get_user = requests.get(default_url() + f'cardholders', headers=default_headers(), params=(("CHType", ch_types()),("lastModifDateTimeStart", last_modify)))
    get_user_json = get_user.json()

    for user in get_user_json:
        if user["CHState"] in ch_states():
            select = read_local_db(user["CHID"])
            if select:
                for result in select:
                    if user["LastModifDateTime"] != result[1]:
                        #user["AuxText05"] = esse
                        put_user = requests.put(default_url() + f'cardholders', headers=default_headers(), json=user, params=(("callAction", False),))
                        update = requests.get(default_url() + f'cardholders/' + str(user["CHID"]), headers=default_headers())
                        user_update = update.json()
                        write_local_db(user["CHID"], user_update["LastModifDateTime"])
                        print("Usuario atualizado " + str(user["CHID"]))
                    else:
                        print(f"N Houve mudança " + str(user["CHID"]))
                        continue    
            else:
                put_user = requests.put(default_url() + f'cardholders', headers=default_headers(), json=user, params=(("callAction", False),))
                update = requests.get(default_url() + f'cardholders/' + str(user["CHID"]), headers=default_headers())
                user_update = update.json()
                insert_local_db(user["CHID"], user_update["LastModifDateTime"])
                print("Usuario Adicionado " + str(user["CHID"]))
        else:
            continue
    #esse =+ 1
    time.sleep(0.3)
    
    finish = datetime.now()
    total = finish - start

    if (total.seconds > 120):
        start_time = True
        delete_local_db()
        print("Clean Table")
    
    else:
        start_time = False