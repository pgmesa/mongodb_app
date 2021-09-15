
def hide(key:int, seed:int) -> int:
    # Hide key in the seed number.
    # WARNING!!!: DONT USE THIS EXAMPLES, ANYONE THAT CAN ACCESS THE PROGRAM
    # SOURCE CODE CAN SEE THIS EXAMPLES AND KNOW HOW YOU HIDE YOUR SECRET KEY

    # Args:
    #     key (int): key to hide
    #     seed (int): seed number generated during encryption

    # Returns:
    #     int: seed number with the key hided
    # ----- Example:
    secret_key_str = str(key)
    seed_str = str(seed)
    seed = int(secret_key_str + seed_str)
    # ------------------------------------------------------------------------
    ...
    
    return seed
    
    
def get(seed:int) -> tuple[int, int]:
    # REVERSES THE 'HIDE' FUNCTION IN ORDER TO GET THE SECRET KEY AND
    # THE CORRECT VALUE OF 'SEED'

    # Args:
    #     seed (int): seed number generated during encryption

    # Returns:
    #     tuple[int, int]: 
    #             First int -> hidden key
    #             Second int -> correct seed number
    # ----- Example 1 solved:
    key = None
    seed_str = str(seed)
    key = int(seed_str[:2])
    seed = int(seed_str[2:])
    # --------------------------------------------------------------------
    ...
    
    return key, seed