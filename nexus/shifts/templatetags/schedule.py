from django.template import Library
from datetime import timedelta

register = Library()

from ..views import color_coder as cc


@register.filter(name="add_datetime")
def add_datetime(original, delta):
    # Handle both timedelta and integer (microseconds) values
    if isinstance(delta, int):
        # Convert microseconds to timedelta
        delta = timedelta(microseconds=delta)
    
    return original + delta

@register.filter(name="color_coder")
def color_coder(position):
    return cc(position)