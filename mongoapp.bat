@echo off

cmd /k "cd -\appvenv\Scripts & activate & cd - & python main.py %* & deactivate & cd %__CD__%"
