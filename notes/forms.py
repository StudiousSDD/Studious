from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Class 
from schedule.models.events import Event 

class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime_local'

class AddClass(ModelForm):
    name = forms.TextInput()
    class Meta:
        model = Class
        fields = ['name']

class AddEvent(ModelForm):
    days_of_week = [
        ("MO", "Monday"),
        ("TU", "Tuesday"),
        ("WE", "Wednesday"),
        ("TH", "Thursday"),
        ("FR", "Friday"),
        ("SA", "Saturday"),
        ("SU", "Sunday"),
    ]
    
    # title = forms.TextInput()
    # start = forms.DateTimeField()
    # end = forms.TextInput()
    # calendar = forms.TextInput() 
    # color_event = forms.TextInput() 
    repeat = forms.MultipleChoiceField(choices=days_of_week, widget=forms.CheckboxSelectMultiple())
    
    class Meta: 
        model = Event
        fields = ['title','start','end','calendar','color_event','end_recurring_period']
        widgets = {
            'start': DateTimeInput(),
            'end': DateTimeInput(),
            'end_recurring_period': DateTimeInput(),
            'color_event': forms.TextInput(attrs={'type': 'color'}),
        }
        labels = {
            'end_recurring_period': _("End Repeat"),
        }