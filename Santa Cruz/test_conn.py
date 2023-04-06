import cx_Oracle


conn_string = 'SERV_INTERFACE_CATRACA/AccCtr0L#2104@oracluster2-scan:1521/TASYPRD'


#connection_string = f'{WxsConn.source_user_name}/{WxsConn.source_pwd_name}@{WxsConn.source_server_name}:{WxsConn.oracle_port}/{WxsConn.source_database_name}'

conn = cx_Oracle.connect(conn_string) # Produção
#print(conn.getinfo(WxsConn.source_server_name))
if conn.version:
    print(conn.version)