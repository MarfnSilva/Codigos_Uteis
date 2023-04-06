-- ============================================================================== --
-- Author: Kelleni Vaikuntha
-- Create date: 16/04/2020
-- Description: Script de Automatização da Associação dos Moradores e Veículos aos Apartamentos
-- Client: Fortknox
-- ============================================================================== --
USE W_Access

------------------------------------------------------------------------------------------
-- DECLARAÇÃO DAS VARIAVEIS --
------------------------------------------------------------------------------------------

DECLARE 
@CHType_Morador			int,
@DataAtual				datetime,
@NivelAtivoID			int,
@NivelInativoID			int,
@NivelAtivoNome			varchar(100),
@NivelInativoNome		varchar(100),
@CHstate_Ativo			int,
@Timezone				int,
@PartitionID			int,
@NivelAcesso_Sol		int,
@NivelAcesso_Agua		int,
@NivelAcesso_Lua		int,
@NivelAcesso_Mirante	int,

@CHID					bigint,
@Firstname				varchar(100),
@CHstate				int, 
@AuxDte10				datetime,
@languageID				int,
@intError				int,
@strError				varchar(50)

SET @CHType_Morador = 2;
SET @DataAtual = CAST(SYSDATETIME() AS DATE); -- Considera só a data, desconsidera as horas
SET @NivelAtivoID = 6; 
SET @NivelInativoID = 9;
SET @CHstate_Ativo = 0; 
SET @Timezone = DATEPArt(Tz,SYSDATETIMEOFFSET());
SET @PartitionID = 1;
SET @NivelAtivoNome = (SELECT TOP 1 AccessLevelName from CfgACAccessLevels WHERE AccessLevelID = @NivelAtivoID);
SET @NivelInativoNome = (SELECT TOP 1 AccessLevelName from CfgACAccessLevels WHERE AccessLevelID = @NivelInativoID);
SET @NivelAcesso_Sol = 1009;
SET @NivelAcesso_Agua = 1012;
SET @NivelAcesso_Lua = 1010;
SET @NivelAcesso_Mirante = 1011
SET @languageID = 2
--Cursor para desassociar e associar nível
DECLARE IMPORT_CURSOR CURSOR FOR

SELECT CHID
FROM CHMAIN
WHERE CHStartValidityDateTime > '2021-04-13 12:49:53.033'

OPEN IMPORT_CURSOR
FETCH NEXT FROM IMPORT_CURSOR
INTO

@CHID

WHILE @@FETCH_STATUS = 0
BEGIN
BEGIN TRANSACTION

------------------------------------------------------------------------------------------
-- Conteúdo da View - Inicio --
------------------------------------------------------------------------------------------
exec wsp_DeleteCardholder @CHID, @languageID, @intError out, @strError out

------------------------------------------------------------------------------------------
-- Conteúdo da View - Fim --
------------------------------------------------------------------------------------------

COMMIT TRANSACTION

FETCH NEXT FROM IMPORT_CURSOR
INTO

@CHID

END
CLOSE IMPORT_CURSOR;
DEALLOCATE IMPORT_CURSOR;
