
import os

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


skf_path = 'server/secret_key.py'
salt = b"\xd5\xc8>7\xd3<}\xf3m\x97r's\xc3Y\x1e"# os.urandom(16)

def _generate_key(password:str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=320000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    return key 

def encrypt_sk_file(password:str):
    key = _generate_key(password)
    fernet = Fernet(key)
    with open(skf_path, 'rb') as file:
        content = file.read()
        encrypted_content = fernet.encrypt(content)
    with open(skf_path, 'wb') as file:  
        file.write(encrypted_content)
    

def decrypt_sk_file(password:str):
    key = _generate_key(password)
    fernet = Fernet(key)
    with open(skf_path, 'rb') as file:
        encrypted_content = file.read()
        decrypted_content = fernet.decrypt(encrypted_content).decode()
    with open(skf_path, 'w') as file:  
        file.writelines(decrypted_content.split('\n'))
        
def check_valid_skf(file_path:str) -> bool:
    return False