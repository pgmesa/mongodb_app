#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from mypy_modules.register import register

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')
    # My own initial tasks for my app (Cada vez que hago cambios en el proyecto
    # se ejecuta este main, ctrl-s)
    ...
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
    # My final tasks (Solo cuando se pare de ejecutar, ctrl-c se ejecuta esto)
    # (una sola vez)
    register.remove()

if __name__ == '__main__':
    main()
