from django import forms

from ..models import (
    Semester,
    Holiday,
    DaySwitch,
)

class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = (
            'term',
            'year',
            'classes_start',
            'classes_end',
        )
        widgets = {
            'classes_start': forms.DateInput(attrs={'class': 'datepicker'}),
            'classes_end': forms.DateInput(attrs={'class': 'datepicker'}),
        }