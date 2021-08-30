@echo off

@REM Eliminamos .bat
echo Eliminando mongoapp.bat...
del "mongoapp.bat"

@REM Eliminamos venv
echo Eliminando entorno virtual...
del /f/q/s appvenv > nul
rmdir /q/s appvenv > nul

echo Eliminando global batch file 'mongoapp.bat'...
call .global.bat --uninstall
@REM Puesto que despues de dr privilegios, se vuelve a ejecutar .global.bat, este archivo y .global se ejecutan
@REM a la vez, por lo que si se ejecuta esto antes que el otro saldra una info erronea, por eso el timeout que solo
@REM se puede romper con control-c
timeout /t 1 /nobreak > nul
@REM Poner parentesis en echo hace que el script llegue a dar error. Toma los parentesis como si fueran del script
@REM y no parentesis como string (evitarlo)
if exist "C:\Windows\System32\mongoapp.bat" (
    echo ERROR: Fallo al desinstalar globalmente la aplicacion -- archivo 'mongoapp.bat' --
    goto failure
) else (
    echo SUCCESS: Aplicacion desinstalada globalmente con exito
    goto success
)

:success
    exit /B 0

:failure
    exit /B 1