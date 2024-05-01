from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div

from crispy_bootstrap5.bootstrap5 import FloatingField

from users.models import PositionChoices

class loadUsersForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(loadUsersForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('load_users'),
            'hx-swap': 'multi:#load-users-message:innerHTML,#load-users-logs:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('file'),
            ),
            Div(
                Submit('submit', 'Load Users', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )
        
class loadPositionsForm(forms.Form):
    file = forms.FileField()
    position = forms.ChoiceField(
        choices=PositionChoices.choices,
    )

    def __init__(self, *args, **kwargs):
        super(loadPositionsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('load_positions'),
            'hx-swap': 'multi:#load-positions-message:innerHTML,#load-positions-logs:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('file'),
                FloatingField('position'),
            ),
            Div(
                Submit('submit', 'Load Positions', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )

class loadCoursesForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(loadCoursesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('load_courses'),
            'hx-swap': 'multi:#load-courses-message:innerHTML,#load-courses-logs:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('file'),
            ),
            Div(
                Submit('submit', 'Load Courses', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )

class loadFacultiesForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(loadFacultiesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('load_faculties'),
            'hx-swap': 'multi:#load-faculties-message:innerHTML,#load-faculties-logs:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('file'),
            ),
            Div(
                Submit('submit', 'Load Faculties', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )

class loadClassesForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(loadClassesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('load_classes'),
            'hx-swap': 'multi:#load-classes-message:innerHTML,#load-classes-logs:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('file'),
            ),
            Div(
                Submit('submit', 'Load Classes', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )
        
class loadFacultyPositionsForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(loadFacultyPositionsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('load_faculty_positions'),
            'hx-swap': 'multi:#load-faculty-positions-message:innerHTML,#load-faculty-positions-logs:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('file'),
            ),
            Div(
                Submit('submit', 'Load Faculty Positions', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )

class loadTutorRoleForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(loadTutorRoleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('load_tutor_roles'),
            'hx-swap': 'multi:#load-tutor-roles-message:innerHTML,#load-tutor-roles-logs:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('file'),
            ),
            Div(
                Submit('submit', 'Load Classes', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )