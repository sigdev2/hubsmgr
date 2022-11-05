cd /d %~dp0
set proga=\"%__CD__%hubsmgr.exe\"
reg add "HKEY_CLASSES_ROOT\*\shell\Sync Hub" /t REG_SZ /v "" /d "Sync Hub" /f
reg add "HKEY_CLASSES_ROOT\*\shell\Sync Hub\command" /t REG_SZ /v "" /d "%proga% \"%%1\"" /f
reg add "HKEY_CLASSES_ROOT\directory\shell\Sync Hub" /t REG_SZ /v "" /d "Sync Hub" /f
reg add "HKEY_CLASSES_ROOT\directory\shell\Sync Hub\command" /t REG_SZ /v "" /d "%proga% \"%%V\"" /f
