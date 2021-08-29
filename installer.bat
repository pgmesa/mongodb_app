@echo off

@REM Ver si python esta instalado
call py --version > nul
if '%errorlevel%' NEQ '0' (
    echo ERROR: Python is not installed, please install it before continuing
    exit /b
)
@REM Ver si pip esta instalado
call pip --version > nul

if '%errorlevel%' NEQ '0' (
    echo ERROR: Python package module 'pip' is not installed, please install it before continuing
    exit /b
)

@REM  Ver si virtualenv esta instalado y si no lo instalamos
call pip show virtualenv > nul
if '%errorlevel%' NEQ '0' (
    echo Instalando virtualenv...
    call pip install virtualenv
    call virtualenv --version
    if '%errorlevel%' NEQ '0' (
        echo El paquete 'virtualenv' no se ha instalado correctamente
        exit /b
    )
)

@REM Crear el virtualenv
set venv_name=appvenv
echo Creando entorno virtual '%venv_name%'...
call virtualenv %venv_name%
call .\%venv_name%\Scripts\activate
echo Instalando dependencias...
call pip install -r requirements.txt
call deactivate

@REM Crear el mongoapp.bat file y moverlo a System32 para su uso global
set batch_file=mongoapp.bat
echo Creando batch file '%batch_file%'...

echo @echo off > %batch_file%
echo set calling_dir=%%cd%% >> %batch_file%
echo cd "%__CD__%appvenv\Scripts" >> %batch_file%
echo call activate >> %batch_file%
echo cd "%__CD__%" >> %batch_file% 
echo call py main.py %%* >> %batch_file%
echo call deactivate >> %batch_file%
echo cd %%calling_dir%% >> %batch_file%

if "%1" == "--local" (
    exit /b
)

echo Instalando globalmente el archivo '%batch_file%'...
:: BatchGotAdmin
:-------------------------------------
REM  --> Check for permissions
    IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
>nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params= %*
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------
@REM     <BATCH SCRIPT HERE>

copy /Y "mongoapp.bat" "C:\Windows\System32\"



