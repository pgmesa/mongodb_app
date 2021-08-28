
import sys

from mypy_modules.process import process

def main():
    
    # Crear virtualenv
    outcome = process.run("", shell=True)

    # Crear mongoapp.bat
    script = ""
    with open('mongoapp.bat', 'w') as file:
        file.write(script)
    
if __name__ == "__main__":
    main()