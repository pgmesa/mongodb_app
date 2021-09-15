
import logging
from mypy_modules.cli import Command, Option, Flag
from server.encryption import decrypt as decrypt_pw

def get_decrypt_cmd() -> Command:
    msg = """
    <password, seed, key> Decrypts a password. 
    Example: -> decrypt "ÌÞÊÞ" 3314316313313263 58
    """
    decrypt = Command(
        'decrypt', description=msg,
        extra_arg=True, mandatory=True, multi=True
    )
    # --------------------------
    mode_opt = def_mode_opt()
    decrypt.add_option(mode_opt)
    
    return decrypt

def def_mode_opt() -> Option:
    msg = """
    <unicode or alphanumx> allows to decrypt with unicode or 
    custom alpha numeric chars. If not set, the progrma tries to 
    decrypt with alphanumx first
    """
    mode = Option(
        '--mode', description=msg,
        extra_arg=True, mandatory=True, choices=["unicode", "alphanumx"]
    )
    
    return mode


decrypt_logger = logging.getLogger(__name__)
def decrypt(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    mode = None
    if "--mode" in options:
        mode = options["--mode"][0]
    encrypted_pw:str = args[0]
    if len(args) == 3:
        try:
            seed = int(args[1])
        except:
            decrypt_logger.error(" La semilla debe ser un entero")
            return
        try:
            key = int(args[2])
        except:
            decrypt_logger.error(" La clave debe ser un entero")
            return
        try:
            password = decrypt_pw(encrypted_pw, seed, key, mode=mode)
        except Exception:
            msg = " Error en la desencriptacion, comprueba los datos introducidos"
            msg += f"\n     {encrypted_pw} {seed} {key}"
            msg += "\n -> Puede que los datos introducidos sean incorrectos y no " 
            msg += "permitan una desencripcion o el modo sea incorrecto"
            decrypt_logger.error(msg)
        else:
            print(f'     -> Encrypted Password: "{encrypted_pw}"')
            print(f'     -> Decrypted Password: "{password}"')
            return
    else:
        msg = " Datos incorrectos\n      "
        msg += "-> Copia y pega los resultados mostrados al encriptar, en el mismo orden"
        decrypt_logger.error(msg)
    print(' - Example  -> decrypt "ÌÞÊÞ" 3314316313313263 58')