
from django import template

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