from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return float(value) * int(arg)

@register.filter
def mul(a, b):
    return a * b
