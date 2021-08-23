@echo off

cd "C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\appvenv\Scripts" & activate
cd "C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app" & python main.py %*
deactivate
@REM __CD__ guarda el directorio del cmd desde el que se llamo a el programa
@REM __APPDIR__ guarda el directorio donde se encuentra el programa .bat que se esta ejecutando
cd %__CD__%