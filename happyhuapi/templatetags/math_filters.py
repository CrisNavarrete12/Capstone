from django import template

register = template.Library()

@register.filter
def minus(value, arg):
    """Resta dos valores numéricos."""
    try:
        return value - arg
    except:
        return 0
