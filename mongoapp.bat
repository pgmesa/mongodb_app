@echo off

if "%1" == "__start__" (
    cmd /k "cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\mongoappenv\Scripts & activate & cd /d    C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app\ & start powershell & python manage.py runserver"
) else (
    cmd /k "cd /d C:\Users\pablo\Desktop\Pablo\Proyectos Python\Probando Django\mongodb_app & python main.py %*"
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