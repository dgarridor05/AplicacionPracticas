from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """
    Splits the string by the argument.
    Usage: {{ value|split:"/" }}
    """
    return value.split(arg)
