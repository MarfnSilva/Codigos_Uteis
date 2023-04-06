--SELECT * FROM CfgSYOperators WHERE OperName = 'marcelo8' or OperName = 'invenzi'

DECLARE @CompanyName varchar(max) = 'Super';
DECLARE @OperID int;
DECLARE @Senha varchar(max) = 'C2E38ED8E641D226AA430895B3093788A65095EEf/rRfyXGnxv9sUWlRiKyNQ=='; -- Senha = mudar123

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
