
import random
from math import floor

def encrypt(password:str, pw_length:int=None, mode:str=None) -> tuple[str, int, int, str]:
    if mode is None:
        try:
            return encrypt_alphanumx(password, pw_length=pw_length)
        except:
            return encrypt_unicode(password, pw_length=pw_length)
    elif mode == 'unicode':
        return encrypt_unicode(password, pw_length=pw_length)
    elif mode == 'alphanumx':
        return encrypt_alphanumx(password, pw_length=pw_length)
    else:
        raise Exception(f" '{mode}' is not a valid mode -> ['unicode', 'alphanumx']")

def decrypt(encrypted:str, seed:int, key:str, mode:str=None) -> str:
    if mode is None:
        try:
            return decrypt_alphanumx(encrypted, seed, key)
        except:
            return decrypt_unicode(encrypted, seed, key)
    elif mode == 'unicode':
        return decrypt_unicode(encrypted, seed, key)
    elif mode == 'alphanumx':
        return decrypt_alphanumx(encrypted, seed, key)
    else:
        raise Exception(f" '{mode}' is not a valid mode -> ['unicode', 'alphanumx']")
    
class EncryptionError(Exception):
    pass
    
# ----------------- ENCRYPT WITH CUSTOM CHARS -----------------
# Can't encrypt all characters, but works with normal password 
# chars. This function works with chars with an unicode number 
# that is less than 10 times the custom chars length:
# -> len(valid_chars)/ord(char_to_encrypt) < 10
# -------------------------------------------------------------
# -> Characters cannot be repeated and more of them
# would create less errors during encrypting strange
# unicode characters
valid_chars = [
    # Numbers
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    # Lower case
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", 
    "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    # Upper Case
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
    "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    # Special Characters Allowed
    "!", "@", "#", "+", "?"
]

def custom_chr(number:int) -> str:
    if number < 0:
        if abs(number) < len(valid_chars):
            index = len(valid_chars) + number
        else:
            if number%len(valid_chars) == 0:
                index = 0
            else:
                index = len(valid_chars)-1 + number%len(valid_chars)
    elif number >= 0:
        if number < len(valid_chars):
            index = number
        else:
            index = number%len(valid_chars)
            
    return valid_chars[index]

def custom_ord(char:str):
    char = str(char)
    return valid_chars.index(char)
    
def get_turns(number:int) -> int:
    return floor(abs(number)/len(valid_chars))

def encrypt_alphanumx(password:str, pw_length:int=None) -> tuple[str, int, int]:
    # Chequeo de que los argumentos son correctos
    if not isinstance(password, str):
        msg = f"The password to encrypt must be a string not '{type(password)}'"
        raise Exception(msg)
    if pw_length is not None:
        if not isinstance(pw_length, int):
            msg = f" The lengh must be an integer not '{type(pw_length)}'"
            raise Exception(msg)
        elif pw_length <= 0:
            raise Exception(" The password length must be greater than 0")
    if len(password) >= 1000000000:
         raise Exception(" The password length can't be >= 10^9 characters")
    # Encriptamos la contraseña
    char_nums = list(map(lambda char: ord(char), password))
    # Comparamos que se puede encriptar el caracter
    for i, char_num in enumerate(char_nums):
        if char_num+198 >= 10*len(valid_chars):
            msg = f" The character {password[i]} can't be encrypted"
            msg += "\n  -> Not enough values in the 'valid_chars' list"
            raise EncryptionError(msg)
    encrypted = ""; seed = ""; key = random.randint(10, 99)
    for char_num in char_nums:
        # Generamos random    
        seed_num  = random.randint(10, 99)
        summ = char_num + seed_num + key
        value = custom_chr(summ)
        seed += str(seed_num) + str(get_turns(summ))
        encrypted += value
    # Cambiamos la longitud
    if pw_length is None:
        compress = -2
        if len(password) == 2:
            compress = -1
        elif len(password) == 1:
            compress = 0
        extra_len = random.randint(compress, 2)
        pw_length = len(password) + extra_len
    else:
        extra_len = pw_length - len(password)
    # Alargamos 
    if extra_len > 0:        
        for _ in range(extra_len):  
            seed_num  = random.randint(10, 99) 
            value = custom_chr(seed_num)
            encrypted += value
    # Comprimimos
    elif extra_len < 0:
        extra_len = extra_len*-1
        compressed_chars = list(encrypted[-extra_len:])
        encrypted = encrypted[:-extra_len]
        compressed_lengths = ""; compressed = ""
        for char in compressed_chars:
            str_val = str(custom_ord(char))
            compressed_lengths += str(len(str_val))
            compressed += str_val
        seed += compressed + compressed_lengths
    num_digitsof_pw_len = len(str(len(password)))
    seed = int(seed+str(len(password)) + str(num_digitsof_pw_len))    
    
    return encrypted, seed, key, 'alphanumx'

def decrypt_alphanumx(encrypted:str, seed:int, key:str):
    # Chequeo de que los argumentos son correctos
    if not isinstance(encrypted, str):
        msg = f"The password to decrypt must be a string not '{type(encrypted)}'"
        raise Exception(msg)
    elif not isinstance(seed, int) or seed <= 0:
        msg = f" The seed must be a positive integer: val='{seed}' type='{type(seed)}'"
        raise Exception(msg)
    elif not isinstance(seed, int) or key <= 0:
        msg = f" The key must be a positive integer: val='{key}' type='{type(key)}'"
        raise Exception(msg)
    # Obtenemos la longitud original de la contraseña y los valores encriptados correctos
    str_seed = str(seed); enc_len = len(encrypted); seed_len = len(str_seed)
    num_digitsof_pw_len = int(str_seed[seed_len-1])
    og_len = int(str_seed[seed_len-1-num_digitsof_pw_len:seed_len-1])
    str_seed = str_seed[:-1-num_digitsof_pw_len]
    if og_len > enc_len:
        compressed_chars = og_len-enc_len
        cp_lengths = str_seed[-compressed_chars:]; str_seed = str_seed[:-compressed_chars]
        start = 0; end = 0
        for i in range(compressed_chars):
            end += int(cp_lengths[i])
            low_range = og_len*3+start
            high_range = og_len*3+end
            start = end
            val = str_seed[low_range:high_range]
            encrypted += custom_chr(int(val))
        str_seed = str_seed[:og_len*3]
    elif og_len < enc_len:
        encrypted = encrypted[:og_len]
    # Desencriptamos
    decrypted = ""; og_nums = []; turns_ = []; seeds = []; ord_chars = []
    for i, char in enumerate(list(encrypted)):
        group = str_seed[i*3:(i+1)*3]
        turns = int(group[2])
        turns_.append(turns); seeds.append(int(group[0:2])); ord_chars.append(custom_ord(char))
        og_num = len(valid_chars)*turns + custom_ord(char) - int(group[0:2]) - key
        og_nums.append(og_num)
        decrypted += chr(og_num)
    
    return decrypted

# -------- ENCRYPT WITH UNICODE CHARS --------
# --------------------------------------------
def encrypt_unicode(password:str, pw_length:int=None) -> tuple[str, int, int]:
    # Chequeo de que los argumentos son correctos
    if not isinstance(password, str):
        msg = f"The password to encrypt must be a string not '{type(password)}'"
        raise Exception(msg)
    if pw_length is not None:
        if not isinstance(pw_length, int):
            msg = f" The lengh must be an integer not '{type(pw_length)}'"
            raise Exception(msg)
        elif pw_length <= 0:
            raise Exception(" The password length must be greater than 0")
    if len(password) >= 1000000000:
         raise Exception(" The password length can't be >= 10^9 characters")
    # Encriptamos la contraseña
    char_nums = list(map(lambda char: ord(char), password))
    encrypted = ""; seed = ""; key = random.randint(10, 99)
    for char_num in char_nums:
        # Generamos random    
        seed_num  = random.randint(10, 99) 
        value = repr(chr(char_num + seed_num + key))
        while len(value)-2 != 1:
            seed_num  = random.randint(10, 99) 
            value = repr(chr(char_num + seed_num + key))
        seed += str(seed_num)
        encrypted += value[1:-1]
    # Cambiamos la longitud
    if pw_length is None:
        compress = -2
        if len(password) == 2:
            compress = -1
        elif len(password) == 1:
            compress = 0
        extra_len = random.randint(compress, 2)
        pw_length = len(password) + extra_len
    else:
        extra_len = pw_length - len(password)
    # Alargamos 
    if extra_len > 0:        
        for _ in range(extra_len):  
            seed_num  = random.randint(10, 99) 
            value = repr(chr(seed_num))
            while len(value)-2 != 1:
                seed_num  = random.randint(10, 99) 
                value = repr(chr(seed_num))
            encrypted += value[1:-1]
    # Comprimimos
    elif extra_len < 0:
        extra_len = extra_len*-1
        compressed_chars = list(encrypted[-extra_len:])
        encrypted = encrypted[:-extra_len]
        compressed_lengths = ""; compressed = ""
        for char in compressed_chars:
            str_val = str(ord(char))
            compressed_lengths += str(len(str_val))
            compressed += str_val
        seed += compressed + compressed_lengths
    num_digitsof_pw_len = len(str(len(password)))
    seed = int(seed+str(len(password)) + str(num_digitsof_pw_len))    
    
    return encrypted, seed, key, 'unicode'                  

def decrypt_unicode(encrypted:str, seed:int, key:str):
    # Chequeo de que los argumentos son correctos
    if not isinstance(encrypted, str):
        msg = f"The password to decrypt must be a string not '{type(encrypted)}'"
        raise Exception(msg)
    elif not isinstance(seed, int) or seed <= 0:
        msg = f" The seed must be a positive integer: val='{seed}' type='{type(seed)}'"
        raise Exception(msg)
    elif not isinstance(seed, int) or key <= 0:
        msg = f" The key must be a positive integer: val='{key}' type='{type(key)}'"
        raise Exception(msg)
    # Obtenemos la longitud original de la contraseña y los valores encriptados correctos
    str_seed = str(seed); enc_len = len(encrypted); seed_len = len(str_seed)
    num_digitsof_pw_len = int(str_seed[seed_len-1])
    og_len = int(str_seed[seed_len-1-num_digitsof_pw_len:seed_len-1])
    str_seed = str_seed[:-1-num_digitsof_pw_len]
    if og_len > enc_len:
        diff = og_len-enc_len
        cp_lengths = str_seed[-diff:]; str_seed = str_seed[:-diff];
        start = 0; end = 0
        for i in range(diff):
            end += int(cp_lengths[i])
            low_range = og_len*2+start
            high_range = og_len*2+end
            start = end
            val = str_seed[low_range:high_range]
            encrypted += chr(int(val))
        str_seed = str_seed[:og_len*2]
    elif og_len < enc_len:
        encrypted = encrypted[:og_len]
    # Desencriptamos
    decrypted = ""
    for i, char in enumerate(list(encrypted)):
        decrypted += chr(ord(char) - int(str_seed[i*2:(i+1)*2]) - key)
    
    return decrypted