from django.template import Library

register = Library()

from ..views import color_coder as cc


@register.filter(name="add_datetime")
def add_datetime(orignal, delta):
    return orignal + delta

@register.filter(name="color_coder")
def color_coder(position):
    return cc(position)