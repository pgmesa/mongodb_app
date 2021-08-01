@echo off

if "%1" == "__start__" (
    @REM start powershell -noexit -command "cmd /k 'cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\mongoappenv\Scripts & activate &    cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\ & python manage.py runserver'"
    @REM start powershell -noexit -command "powershell -command 'cd /d C:\Users\pablo\Desktop'; powershell 'commands'"
    start cmd /k "cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\appvenv\Scripts & activate &    cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\ & python manage.py runserver & exit"
) else (
    cd "C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\appvenv\Scripts" & activate
    cd "C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app" & python main.py %*
    deactivate
    cd %__CD__%
)