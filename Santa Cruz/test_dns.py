import cx_Oracle

conn_string = 'SERV_INTERFACE_CATRACA/AccCtr0L#2104@oracluster2-scan:1521/TASYPRD'

# Establish the database connection
connection = cx_Oracle.connect(user="SERV_INTERFACE_CATRACA", password='AccCtr0L#2104',
                               dsn="oracluster2-scan:1521/TASYPRD")

# Obtain a cursor
cursor = connection.cursor()