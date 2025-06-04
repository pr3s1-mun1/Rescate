# extra_tags.py
from django import template
from collections import defaultdict

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un valor de un diccionario o retorna 0 si no existe"""
    if isinstance(dictionary, defaultdict):
        return dictionary.get(key, 0)
    return dictionary.get(key, 0)

@register.filter
def sum_row(dictionary):
    """Suma los valores de un diccionario, manejando defaultdicts"""
    if isinstance(dictionary, defaultdict):
        dictionary = dict(dictionary)
    return sum(dictionary.values()) if dictionary else 0

@register.filter
def sum_column(conteos, base):
    """Suma los valores de una columna específica"""
    total = 0
    for tipo_dict in conteos.values():
        if isinstance(tipo_dict, defaultdict):
            total += tipo_dict.get(base, 0)
        else:
            total += tipo_dict.get(base, 0)
    return total

@register.filter
def grand_total(conteos):
    """Calcula el total general de todos los valores"""
    total = 0
    for tipo_dict in conteos.values():
        if isinstance(tipo_dict, defaultdict):
            total += sum(tipo_dict.values())
        else:
            total += sum(tipo_dict.values())
    return total

@register.filter
def dict_get(d, key):
    """Obtiene un valor de un diccionario (funciona también con defaultdict)."""
    return d.get(key, {})

@register.filter
def dict_getPac(diccionario, clave):
    return diccionario.get(clave, 0)