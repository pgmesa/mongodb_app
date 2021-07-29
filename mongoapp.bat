@echo off

if "%1" == "__start__" (
    @REM start powershell -noexit -command "cmd /k 'cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\mongoappenv\Scripts & activate &    cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\ & python manage.py runserver'"
    @REM start powershell -noexit -command "powershell -command 'cd /d C:\Users\pablo\Desktop'; powershell 'commands'"
    start cmd /k "cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\mongoappenv\Scripts & activate &    cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\ & python manage.py runserver & exit"
) else (
    @REM No aparece la info del server en la primera powershell porque esa esta ocupada con la que esta ejecutando el main
    @REM hay o que ejecutar otra o conectar las salidas
    cd C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app
    python main.py %*
)

@REM cmd \k "cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app"
@REM cmd \k  ".\mongoappenv\Scripts\activate"
@REM @REM cmd \k python main.py %*
@REM cmd \k "start powershell"
@REM cmd \k "python manage.py runserver"
@REM @REM cmd \k deactivate

@REM if "%1" == "start" (
@REM     SET go_to_dir = cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\mongoappenv\Scripts
@REM     SET activate_venv = activate
@REM     SET go_to_appdir = cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\
@REM     SET start_new_pws = start powershell
@REM     SET start_app = python manage.py runserver
@REM     SET "order=%go_to_dir% & %activate_venv% & %go_to_appdir% & %start_new_pws% & %start_app%"
@REM     echo %order%
@REM     cmd /k %order%