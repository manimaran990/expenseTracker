from django import template

register = template.Library()

@register.filter
def ifequal(value, arg):
    return value == arg