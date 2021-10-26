
import os
from django import template
from mypy_modules.register import register as reg

register = template.Library()

@register.filter
def lookup(dictionary:dict, key):
    return dictionary.get(key, "")

@register.filter
def lookup2(key, dictionary:dict):
    return dictionary.get(key, "")

@register.filter
def times(number:int):
    return range(number)

@register.filter
def addstr(str1:str, str2:str):
    return str1 + str2

@register.filter
def autocomplete(action:str):
    r = reg.load()
    if r is not None and "autocomplete" in r:
        return "on"
    return "off"

@register.filter
def get_type(tp:str):
    if tp == 'password':
        return 'password'
    return 'text'

@register.filter
def is_theme(theme:str):
    real_theme = reg.load("theme")
    if (real_theme is None and theme == 'light') or theme == real_theme:
        return True
    return False

@register.filter
def cipherfile_added(ignore) -> bool:
    if os.path.exists('server/cipher_lib/cipher.py'):
        return True
    return False