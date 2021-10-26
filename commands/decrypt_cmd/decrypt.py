
import logging

from mypy_modules.cli import Command, Option, Flag
from server.encryption_lib.encryption import (
    decrypt as decrypt_pw, derive_password, generate_key,
    InvalidToken
)

def get_decrypt_cmd() -> Command:
    msg = """<token> <key> decrypts data"""
    decrypt = Command(
        'decrypt', description=msg,
        extra_arg=True, mandatory=True, multi=True
    )
    # --------------------------
    derive_opt = def_derive_opt()
    decrypt.add_option(derive_opt)
    
    return decrypt

def def_derive_opt() -> Option:
    msg = """<password> derives the password to obtain the
    key needed by the algorithm to decrypt the token (encrypted data).
    If this option is used, the second main argument 'key' is ignored
    """
    derive = Option(
        '--derive', description=msg,
        extra_arg=True, mandatory=True
    )
    
    return derive


decrypt_logger = logging.getLogger(__name__)
def decrypt(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    if "--derive" in options:
        password = options["--derive"][0]
        key = derive_password(password)
    else:
        key = args[1]
    token:str = args[0]
    try:
        data = decrypt_pw(token.encode(), key)
    except InvalidToken:
        print(" + ERROR DURING DECRYPTION:")
        print("     - The key is incorrect")
    else:
        print(" + DECRYPTION SUCCESSFUL:")
        print(f'    - Decrypted data -> "{data}"')
    
   
    
    
    
    