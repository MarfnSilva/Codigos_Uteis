import pyodbc
import pandas as pd

servername = 'NSP-USU-0098\W_ACCESS'
userid = 'sa'
password = '#w_access_Adm#'
databasename = 'W_Access'

cnxn = pyodbc.connect('Driver={SQL Server};Server='+servername+';UID='+userid+';PWD='+password+';Database='+databasename)
pd.read_sql('SELECT top 1000 * FROM CHMain',cnxn).to_excel('CHMain_Results.xlsx')

# cursor = cnxn.cursor()
# script = """
# SELECT top 45 * FROM CHMain
# """

# cursor.execute(script)

# columns = [desc[0] for desc in cursor.description]
# data = cursor.fetchall()
# df = pd.DataFrame([tuple(t) for t in cursor.fetchall()], columns=[columns])

# writer = pd.ExcelWriter('CHMain_Results.xlsx')
# df.to_excel(writer, sheet_name='bar')
# writer.save()


