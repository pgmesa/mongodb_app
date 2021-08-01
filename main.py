
import sys
import platform
import logging
from commands.mongoapp import mongoapp, get_mongoapp_cmd
from mypy_modules.cli import Cli, CmdLineError

logging.basicConfig(level=logging.NOTSET)
main_logger = logging.getLogger(__name__)
def main():
    cli = Cli(get_mongoapp_cmd(), def_advanced_help=True)
    try:
        args_processed = cli.process_cmdline(sys.argv)
        os = platform.system()
        if os != "Windows":
            err_msg = f" Este programa no soporta '{os}':OS"
            main_logger.critical(err_msg)
            exit(1)
        print(); main_logger.info(" Programa iniciado")
        mongoapp(**args_processed)
    except CmdLineError as err:
        main_logger.error(f" {err}"); exit(1)
    else:
        main_logger.info(" Programa finalizado correctamente")
        print()

if __name__ == "__main__":
    main()