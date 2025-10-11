from django import template
from decimal import Decimal
from datetime import timedelta

register = template.Library()

@register.filter
def hours(value):
    # Handle both timedelta and integer (microseconds) values
    if isinstance(value, int):
        # Convert microseconds to timedelta
        value = timedelta(microseconds=value)
    
    if hasattr(value, 'total_seconds'):
        hours = value.total_seconds() / 3600
        return f"{hours:.2f}"
    
    # Fallback for unexpected types
    return str(value)

@register.filter
def multiply(value, arg):
    # Handle both timedelta and integer (microseconds) values
    if isinstance(value, int):
        # Convert microseconds to timedelta
        value = timedelta(microseconds=value)
    
    if hasattr(value, 'total_seconds'):
        ans = Decimal.from_float(value.total_seconds() / 3600) * arg
        return f"{ans:.2f}"
    
    # Fallback for unexpected types
    return str(value)