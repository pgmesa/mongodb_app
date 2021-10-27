
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


skf_path = 'server/secret_key.py'
salt = b"\xd5\xc8>7\xd3<}\xf3m\x97r's\xc3Y\x1e" # import os; os.urandom(16)

def derive_password(password:str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=320000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    return key 

def generate_key(password:str=None) -> bytes:
    if password is None:
        return Fernet.generate_key()
    else:
        return derive_password(password)

def encrypt(text:str, key:bytes) -> bytes:
    fernet = Fernet(key)
    token = fernet.encrypt(text.encode())
    
    return token

def decrypt(token:bytes, key:bytes) -> str:
    fernet = Fernet(key)
    decrypted = fernet.decrypt(token).decode()
    
    return decrypted

def encrypt_file(file_path:str, password:str, override:bool=True):
    key = derive_password(password)
    with open(file_path, 'rb') as file:
        token = encrypt(file.read().decode(), key)
    if not override:
        filename, extension, dirpath = split_path(file_path)
        file_path = dirpath+filename+"_encrypted"+extension
    with open(file_path, 'wb') as file:  
        file.write(token)
    
def decrypt_file(file_path:str, password:str, override:bool=True):
    key = derive_password(password)
    with open(file_path, 'rb') as file:
        content = decrypt(file.read(), key)
    if not override:
        filename, extension, dirpath = split_path(file_path)
        file_path = dirpath+filename+"_encrypted"+extension
    with open(file_path, 'w') as file:
        file.writelines(content.split('\n'))
        
def get_sha256_hash(string:str) -> str:
    return hashlib.sha256(string.encode()).hexdigest()


# -------------------- Complementary Functions ----------------------
# -------------------------------------------------------------------
def split_path(file_path:str):
    file_fullname = ""; dirpath = ""
    file_path = file_path.replace("\\", "/")
    
    def _split_file_name(file_fullname:str):
        if '.' not in file_fullname:
            filename = file_fullname
            extension = ""
        else:
            splitted = file_fullname.split('.')
            extension = "."+splitted[len(splitted)-1]
            filename = file_fullname.removesuffix(extension)
        if filename == "" and extension != "":
            filename = extension
            extension = ""
            
        return filename, extension
    
    if "/" not in file_path:
        file_fullname = file_path
        filename, extension = _split_file_name(file_fullname)
    else:
        for i, char in enumerate(file_path[::-1]):
            if char == "/":
                filename, extension = _split_file_name(file_fullname[::-1])
                dirpath = file_path[:-i]
                break
            file_fullname += char
    
    return filename, extension, dirpath
