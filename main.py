
import sys
import logging
from commands.mongoapp import mongoapp, get_mongoapp_cmd
from mypy_modules.cli import Cli, CmdLineError

logging.basicConfig(level=logging.NOTSET)
main_logger = logging.getLogger(__name__)
def main():
    cli = Cli(get_mongoapp_cmd(), def_advanced_help=True)
    try:
        args_processed = cli.process_cmdline(sys.argv)
        mongoapp(**args_processed)
    except CmdLineError as err:
        main_logger.error(f" {err}"); exit(1)

if __name__ == "__main__":
    print("Programa iniciado")
    main()