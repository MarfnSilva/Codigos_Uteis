CREATE TABLE #DADOS
(
Nome				varchar(150), -- FirstName
Matricula			varchar(50), -- IdNumber
Data_de_Nascimento	varchar(50), -- AuxDte01
CPF					varchar(50), -- AuxText01
Telefone			varchar(50), -- AuxText02
Email				varchar(50), -- Email
Departamento		varchar(50)  -- AuxLst01
)

-- INSERINDO DADOS DO ARQUIVO NA TABELA DE IMPORTAÇÃO
BULK INSERT #DADOS
FROM 'C:\Usuarios.csv' -- ALTERAR CONFORME LOCALIDADE DA PASTA SALVA
WITH
(CODEPAGE = 'ACP',
FIELDTERMINATOR = ';',
FIRSTROW = 2,
ROWTERMINATOR = '\n'
)

SELECT Data_de_Nascimento, TRY_CONVERT(date,TRY_CONVERT(date,TRY_CONVERT(date,Data_de_Nascimento,103),104),105) AS dataConvert FROM #DADOS
Drop table #DADOS
