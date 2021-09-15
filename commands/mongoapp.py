
from contextlib import suppress
import logging
from commands.upload_cmd.upload import upload
from mypy_modules.cli import Command, Flag, Option
# imports de los comandos asociados
from .open_cmd.open import open_, get_open_cmd
from .start_cmd.start import get_start_cmd, start
from .launch_cmd.launch import get_launch_cmd, launch
from .upload_cmd.upload import get_upload_cmd, upload
from .restore_cmd.restore import get_restore_cmd, restore
from .register_cmd.register import get_register_cmd, register
from .repo_cmd.repo import get_repo_cmd, repo
from .clear_cmd.clear import get_clear_cmd, clear
from .encrypt_cmd.encrypt import encrypt, get_encrypt_cmd
from .decrypt_cmd.decrypt import decrypt, get_decrypt_cmd
from configs.settings import BASE_DIR
from mypy_modules.process import process
from mypy_modules.register import register as config_reg

def get_mongoapp_cmd() -> Command:
    msg = """
    allows to interact with the mongoapp
    """
    mongoapp = Command(
        'mongoapp', description=msg
    )
    # ++++++++++++++++++++++++++++++++
    open_cmd = get_open_cmd()
    mongoapp.nest_cmd(open_cmd)
    # ++++++++++++++++++++++++++++++++
    start_cmd = get_start_cmd()
    mongoapp.nest_cmd(start_cmd)
    # ++++++++++++++++++++++++++++++++
    launch_cmd = get_launch_cmd()
    mongoapp.nest_cmd(launch_cmd)
    # ++++++++++++++++++++++++++++++++
    upload_cmd = get_upload_cmd()
    mongoapp.nest_cmd(upload_cmd)
    # ++++++++++++++++++++++++++++++++
    restore_cmd = get_restore_cmd()
    mongoapp.nest_cmd(restore_cmd)
    # ++++++++++++++++++++++++++++++++
    register_cmd = get_register_cmd()
    mongoapp.nest_cmd(register_cmd)
    # ++++++++++++++++++++++++++++++++
    repo_cmd = get_repo_cmd()
    mongoapp.nest_cmd(repo_cmd)
    # ++++++++++++++++++++++++++++++++
    clear_cmd = get_clear_cmd()
    mongoapp.nest_cmd(clear_cmd)
    # ++++++++++++++++++++++++++++++++
    encrypt_cmd = get_encrypt_cmd()
    mongoapp.nest_cmd(encrypt_cmd)
    # ++++++++++++++++++++++++++++++++
    decrypt_cmd = get_decrypt_cmd()
    mongoapp.nest_cmd(decrypt_cmd)
    # --------------------------------
    dir_opt = def_dir_opt()
    mongoapp.add_option(dir_opt)
    # --------------------------------
    reveal_opt = def_reveal_opt()
    mongoapp.add_option(reveal_opt)
    # --------------------------------
    cmd_opt = def_cmd_opt()
    mongoapp.add_option(cmd_opt)
    # --------------------------------
    uninstall_info_opt = def_uninstall_info_opt()
    mongoapp.add_option(uninstall_info_opt)
    # --------------------------------
    enable_opt = def_enable_opt()
    mongoapp.add_option(enable_opt)
    # --------------------------------
    disable_opt = def_disable_opt()
    mongoapp.add_option(disable_opt)

    return mongoapp

def def_dir_opt() -> Option:
    msg = """shows the directory where the app is located"""
    dir_ = Option(
        '--dir', description=msg
    )
    
    return dir_

def def_reveal_opt() -> Option:
    reveal = Option(
        '--reveal', description='reveals the app in the file explorer'
    )
    
    return reveal
    
def def_cmd_opt() -> Option:
    msg = """
    opens a cmd in the app location directory
    """
    cmd = Option(
        '--cmd', description=msg
    )

    return cmd

def def_uninstall_info_opt() -> Option:
    msg = """
    shows info about the steps to follow in order to uninstall and delete
    the app information in the current computer
    """
    uninstall_info = Option(
        '--uninstall-info', description=msg
    ) 
    
    return uninstall_info

def def_enable_opt() -> Option:
    enable = Option(
        '--enable-autocomplete', description='enables autocomplete in html forms'
    )
    
    return enable

def def_disable_opt() -> Option:
    disable = Option(
        '--disable-autocomplete', description='disables autocomplete in html forms'
    )
    
    return disable


mongoapp_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
# -------------------------------------------------------------------- 
def mongoapp(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    # Procesamos las opciones
    if "--dir" in options:
        print(f"     + App Location --> '{BASE_DIR}'")
        return
    elif "--reveal" in options:
        process.Popen(f'start %windir%\explorer.exe "{BASE_DIR}"', shell=True)
        return
    elif "--cmd" in options:
        location = f'{BASE_DIR}'
        process.Popen(f'start cmd /k "cd {location} & deactivate"', shell=True)
        return
    elif "--enable-autocomplete" in options:
        with suppress(Exception):
            config_reg.add('autocomplete', True)
        mongoapp_logger.info(" Autocompletado en formularios activado")
        return
    elif "--disable-autocomplete" in options:
        with suppress(Exception):
            config_reg.remove('autocomplete')
        mongoapp_logger.info(" Autocompletado en formularios desactivado")
        return
    elif "--uninstall-info" in options:
        msg = """
        In order to delete the app and its information (irreversibly) from 
        the computer follow this steps:
        1. Close the server and make sure the app is not running
        2. Open a cmd and type 'mongoapp clear -y'
        3. Type 'mongoapp --cmd'
        4. In the new cmd window that the step 3 has openned, execute the 
           uninstall.bat file
        Now every sensitive information has been deleted. If you want to 
        delete the empty app as well, just delete the mongodb_app directory
        """
        print(msg)
        return
    # Procesamos los comandos anidados
    if "open" in nested_cmds:
        cmd_info = nested_cmds.pop("open")
        open_(**cmd_info)
    elif "start" in nested_cmds:
        cmd_info = nested_cmds.pop("start")
        start(**cmd_info)
    elif "launch" in nested_cmds:
        cmd_info = nested_cmds.pop("launch")
        launch(**cmd_info)
    elif "upload" in nested_cmds:
        cmd_info = nested_cmds.pop("upload")
        upload(**cmd_info)
    elif "restore" in nested_cmds:
        cmd_info = nested_cmds.pop("restore")
        restore(**cmd_info)
    elif "register" in nested_cmds:
        cmd_info = nested_cmds.pop("register")
        register(**cmd_info)
    elif "repo" in nested_cmds:
        cmd_info = nested_cmds.pop("repo")
        repo(**cmd_info)
    elif "clear" in nested_cmds:
        cmd_info = nested_cmds.pop("clear")
        clear(**cmd_info)
    elif "encrypt" in nested_cmds:
        cmd_info = nested_cmds.pop("encrypt")
        encrypt(**cmd_info)
    elif "decrypt" in nested_cmds:
        cmd_info = nested_cmds.pop("decrypt")
        decrypt(**cmd_info)
    else:
        print("     Aplicacion para gestionar Bases de Datos de MongoDB")
        print("     Intoduce -h para desplegar la ayuda")
        
    