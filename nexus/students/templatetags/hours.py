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

@register.filter
def duration(value):
    """
    Format a duration (timedelta or integer microseconds) as hours:minutes
    """
    if isinstance(value, int):
        # Convert microseconds to timedelta
        value = timedelta(microseconds=value)
    
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}:{minutes:02d}"
    
    return str(value)