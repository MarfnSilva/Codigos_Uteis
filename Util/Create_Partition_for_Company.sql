
USE W_ACCESS
--DECLARE @CompanyID int; -- = 2;

SET @CompanyID = CAST($CompanyID as int);

DECLARE @CompanyName varchar(max);
DECLARE @CompanySistema int; 
DECLARE @CompanyPedestre int;
DECLARE @CompanyVeiculos int;
DECLARE @CompanyCadastro int;
DECLARE @CompanyEstacionamento int;
DECLARE @CompanyUsuarios int;
DECLARE @PartAtual int;
DECLARE @OperID int;
DECLARE @Senha varchar(max) = 'C2E38ED8E641D226AA430895B3093788A65095EEf/rRfyXGnxv9sUWlRiKyNQ=='; -- Senha = mudar123

DECLARE @CompanyGroup int;
	DECLARE @AcessoPedestre int;
		DECLARE	@TorreNorte int;
			DECLARE @TN_Catracas int;
			DECLARE @TN_ElevadorServGaragem int;
			DECLARE @TN_ElevadorServAndares int;
			DECLARE @TN_NivelBasico int;
			DECLARE @TN_VIP2SS int;
		DECLARE @TorreSul int;
			DECLARE @TS_Catracas int;
			DECLARE @TS_ElevadorServGaragem int;
			DECLARE @TS_ElevadorServAndares int;
			DECLARE @TS_NivelBasico int;
			DECLARE @TS_VIP2SS int;
	DECLARE @Veiculos int; 
		DECLARE @Comum int;
		DECLARE @Extra int; 
		DECLARE @Vip int;
			DECLARE @VipTorreNorte int;
			DECLARE @VipTorreSul int;




--Constantes
DECLARE 
@PartitionTypeSistema int = 0,
@PartitionTypeUsuario int = 1



SELECT  @CompanyName = CompanyName FROM CHCompanies where Companyid = @CompanyID
PRINT @CompanyName 


-- Verifica e cria Partições 

IF NOT EXISTS (SELECT * FROM CHCompanies WHERE CompanyID = @CompanyID AND CompanyName like 'Cond.%')
BEGIN

	--====== '['+ @CompanyName +'] Sistema') ======--
	IF NOT Exists (SELECT * FROM CfgSYPartitions WHERE strlanguage2 LIKE '['+ @CompanyName +'] Sistema')
		BEGIN
			PRINT 'Partição: ['+ @CompanyName +'] Sistema.Não existe'
			INSERT INTO CfgSYPartitions
			VALUES (@PartitionTypeSistema, '['+ @CompanyName +'] Sistema', '['+ @CompanyName +'] Sistema', '['+ @CompanyName +'] Sistema', '['+ @CompanyName +'] Sistema', '','','','',0,0, null, null, null, null, 587, 5, null, null, null, null )

			SELECT @CompanySistema = PartitionID FROM CfgSYPartitions WHERE strLanguage2 like '['+ @CompanyName +'] Sistema'

			UPDATE CHCompanies 	
			SET PartitionID = @CompanySistema
			WHERE CompanyID = @CompanyID
			PRINT @CompanySistema;
		END
	ELSE 
		BEGIN	

			SELECT @CompanySistema = PartitionID FROM CfgSYPartitions WHERE strLanguage2 like '['+ @CompanyName +'] Sistema'
			IF NOT EXISTS (SELECT  * FROM CHCompanies where Companyid = @CompanyID AND PartitionID = @CompanySistema)
				UPDATE CHCompanies 	
				SET PartitionID = @CompanySistema
				WHERE CompanyID = @CompanyID
			PRINT @CompanySistema;
		END
	--====== '['+ @CompanyName +'] Usuarios') ======--
	IF NOT Exists (SELECT * FROM CfgSYPartitions WHERE strlanguage2 LIKE '['+ @CompanyName +'] Usuarios')
		BEGIN
			PRINT 'Partição: ['+ @CompanyName +'] Usuarios.Não existe'
			INSERT INTO CfgSYPartitions
			VALUES (@PartitionTypeUsuario, '['+ @CompanyName +'] Usuarios', '['+ @CompanyName +'] Usuarios', '['+ @CompanyName +'] Usuarios', '['+ @CompanyName +'] Usuarios', '','','','',0,0, 3, null, null, null, 587, 5, 4, null, null, null )

			SELECT @CompanyUsuarios = PartitionID FROM CfgSYPartitions WHERE strLanguage2 like '['+ @CompanyName +'] Usuarios'
			PRINT @CompanyUsuarios;
		END
	ELSE 
		BEGIN	

			SELECT @CompanyUsuarios = PartitionID FROM CfgSYPartitions WHERE strLanguage2 like '['+ @CompanyName +'] Usuarios'
			PRINT @CompanyUsuarios;
		END
	--====== Add Operator ======--
	IF NOT EXISTS (SELECT * FROM CfgSYOperators WHERE OperName = @CompanyName)
	BEGIN
		SET IDENTITY_INSERT CfgSYOperators off
		INSERT INTO CfgSYOperators (OperName, OperFullName, Password, ProfileID, MultiUser, Enabled, MustChangePassword, LanguageID, Culture, AccountType)
		VALUES (@CompanyName, @CompanyName, @Senha, 1, 1, 1, 1, 2, 'pt-BR', 1)
		SET IDENTITY_INSERT CfgSYOperators on
		SELECT @OperID = OperID FROM CfgSYOperators WHERE OperName = @CompanyName
		INSERT INTO CfgSYOperatorTerminals
		VALUES (@OperID, 1)
		INSERT INTO CfgSYOperatorAccessTimes
		VALUES (@OperID, 1)
		INSERT INTO CfgSYOperatorPasswordHistory
		VALUES (@OperID, @Senha, '2021-09-16 10:24:55.050')
		PRINT @OperID
	END
ELSE
	BEGIN
		PRINT 'TESTE'
	END
END