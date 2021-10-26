
import logging
from mypy_modules.cli import Command, Option, Flag
from server.encryption_lib.encryption import (
    encrypt as encrypt_pw, generate_key, derive_password
)

def get_encrypt_cmd() -> Command:
    msg = """
    <data> encrypts data
    """
    encrypt = Command(
        'encrypt', description=msg,
        extra_arg=True, mandatory=True
    )
    # --------------------------
    with_opt = def_with_opt()
    encrypt.add_option(with_opt)
    
    return encrypt

def def_with_opt():
    msg = """
    <password> encrypts the text deriving the key from the password 
    """
    with_opt = Option(
        '--with', description=msg,
        extra_arg=True, mandatory=True, convert_ints=True
    )
    
    return with_opt


encrypt_logger = logging.getLogger(__name__)
def encrypt(args:list=[], options:dict={}, flags:list=[], nested_cmds:dict={}):
    # Procesamos opciones
    if "--with" in options:
        pw = options["--with"][0]
        key = derive_password(pw)
    else:
        key = generate_key()

    data = args[0]
    token = encrypt_pw(data, key)
    
    print(" + WARNING!!: THE FOLLOWING DATA IS NECESSARY TO REVERSE THE ENCRYPTION")
    if locals().get('pw', None) is not None:
        print(f'    - Password: "{pw}"')
    else:
        print(f'    - Key: "{key.decode()}"')
    print(f'    - Token (encrypted data): "{token.decode()}"')