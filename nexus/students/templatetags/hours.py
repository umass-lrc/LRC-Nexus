from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def hours(value):
    hours = value.total_seconds() / 3600
    return f"{hours:.2f}"

@register.filter
def multiply(value, arg):
    ans = Decimal.from_float(value.total_seconds() / 3600) * arg
    return f"{ans:.2f}"