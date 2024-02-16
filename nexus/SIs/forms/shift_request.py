from django import forms
from django.urls import reverse
from django.contrib.admin import widgets 

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, HTML
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import  BS5Accordion, FloatingField

from dal import autocomplete

from users.models import (
    Positions,
)

from ..models import (
    SIRoleInfo,
)
