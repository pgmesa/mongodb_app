
from django import template

register = template.Library()

@register.filter
def lookup(dictionary:dict, key):
    return dictionary.get(key, None)