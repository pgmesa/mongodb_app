
import logging
from mypy_modules.cli import Command, Option, Flag
from server.encryption import decrypt as decrypt_pw, encrypt as encrypt_pw


def get_encrypt_cmd() -> Command:
    msg = """
    <password> Encrypts a password
    """
    encrypt = Command(
        'encrypt', description=msg,
        extra_arg=True, mandatory=True
    )
    # --------------------------
    len_opt = def_len_opt()
    encrypt.add_option(len_opt)
    # --------------------------
    mode_opt = def_mode_opt()
    encrypt.add_option(mode_opt)
    
    return encrypt

def def_len_opt():
    msg = """
    <password_length> creates a password with the number 
    of unicode chars specified (some characters could appear escaped)
    """
    length = Option(
        '--len', description=msg,
        extra_arg=True, mandatory=True, convert_ints=True
    )
    
    return length

def def_mode_opt() -> Option:
    msg = """
    <unicode or alphanumx> allows to encrypt with unicode or 
    custom alpha numeric chars. If not set, the progrma tries to 
    encrypt with alphanumx first
    """
    mode = Option(
        '--mode', description=msg,
        extra_arg=True, mandatory=True, choices=["unicode", "alphanumx"]
    )
    
    return mode


encrypt_logger = logging.getLogger(__name__)
def encrypt(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    # Procesamos opciones
    length = None; mode = None
    if "--len" in options:
        length = options["--len"][0]
    if "--mode" in options:
        mode = options["--mode"][0]
    # Procesamos comandos anidados
    password = args[0]
    try:
        encryption = encrypt_pw(password, pw_length=length, mode=mode)
        decr_pw = decrypt_pw(*encryption)
        if decr_pw != password:
            encrypt_logger.error(" No se ha podido generar una contraseña")
            return  
    except Exception as err:
        encrypt_logger.error(err)
        return
    
    print(f' + Password: "{password}"')
    print(f" + Encrypting mode: {encryption[3]}")
    print(" + WARNING!!: THE FOLLOWING DATA IS NECESSARY TO REVERSE THE ENCRYPTION")
    print(f'    - Encrypted password: "{encryption[0]}"')
    print("     - Seed Numer: ", encryption[1])
    print("     - key: ", encryption[2])
    
    return encryption