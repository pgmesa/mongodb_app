@echo off

@REM Ver si python esta instalado
call python --version > nul
if '%errorlevel%' NEQ '0' (
    echo ERROR: Python is not installed, please install it before continuing
    goto failure
)
@REM Ver si pip esta instalado
call pip --version > nul

if '%errorlevel%' NEQ '0' (
    echo ERROR: Python package module 'pip' is not installed, please install it before continuing
    goto failure
)

@REM  Ver si virtualenv esta instalado y si no lo instalamos
call pip show virtualenv > nul
if '%errorlevel%' NEQ '0' (
    echo Instalando virtualenv...
    call pip install virtualenv
)

@REM Crear el virtualenv
set venv_name=appvenv
echo Creando entorno virtual '%venv_name%'...
call python -m virtualenv %venv_name%
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
echo call python main.py %%* >> %batch_file%
echo call deactivate >> %batch_file%
echo cd %%calling_dir%% >> %batch_file%

echo SUCCESS: Aplicacion instalada localmente con exito 
echo -- Introduce 'mongoapp.bat launch' en el directorio de la aplicacion para iniciarla --
if "%1" == "--local" (
    goto success
)

echo Instalando globalmente el archivo '%batch_file%'...
call .global.bat --install
@REM Puesto que despues de dr privilegios, se vuelve a ejecutar .global.bat, este archivo y .global se ejecutan
@REM a la vez, por lo que si se ejecuta esto antes que el otro saldra una info erronea, por eso el timeout que solo
@REM se puede romper con control-c
timeout /t 1 /nobreak > nul
if exist "C:\Windows\System32\mongoapp.bat" (
    echo SUCCESS: Aplicacion instalada globalmente con exito 
    echo -- introduce 'mongoapp launch' para iniciar la aplicacion --
    goto success
) else (
    echo ERROR: Fallo al instalar globalmente el archivo 'mongoapp.bat'
    goto failure
)

:success
    exit /B 0

:failure
    exit /B 1