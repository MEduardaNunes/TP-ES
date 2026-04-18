from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retorna o valor de um dicionário pela chave."""
    return dictionary.get(key)