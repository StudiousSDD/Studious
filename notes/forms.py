from django.forms import ModelForm, Form
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Class 
from schedule.models.events import Event 

days_of_week = [
    ("MO", "Monday"),
    ("TU", "Tuesday"),
    ("WE", "Wednesday"),
    ("TH", "Thursday"),
    ("FR", "Friday"),
    ("SA", "Saturday"),
    ("SU", "Sunday"),
]

class AddClass(ModelForm):
    name = forms.TextInput()
    class Meta:
        model = Class
        fields = ['name']

class AddEvent(ModelForm):
    color_widget  = forms.TextInput(attrs={'type': 'range', 'min': 0, 'max': 359, 'step': 1, 'class': 'slider'})
    color = forms.IntegerField(min_value=0, max_value=359, widget=color_widget)
    
    repeat = forms.MultipleChoiceField(choices=days_of_week, widget=forms.CheckboxSelectMultiple())
    
    class Meta: 
        model = Event
        fields = ['title','start','end','calendar','end_recurring_period',]
        widgets = {
            'start': forms.TextInput(attrs={'type': 'datetime-local'}),
            'end': forms.TextInput(attrs={'type': 'datetime-local'}),
            'end_recurring_period': forms.TextInput(attrs={'type': 'date'}),
        }
        labels = {
            'end_recurring_period': _("End Repeat"),
        }

class ImportEvent(ModelForm):
    file = forms.FileField()
    class Meta:
        model = Event
        fields = ['calendar', 'file']
        widgets = {
            'calendar': forms.HiddenInput(),
        }
        
class EditEventForm(ModelForm):    
    def __init__(self, *args, **kwargs):
        hue = kwargs.pop('hue', None)
        super(EditEventForm, self).__init__(*args, **kwargs)
        if not hue:
            hue = 180
        color_widget = forms.TextInput(attrs={'type': 'range', 'min': 0, 'max': 359, 'step': 1, 'value': hue, 'class': 'slider'})
        self.fields["color"] = forms.IntegerField(min_value=0, max_value=359, widget=color_widget)
            

    class Meta: 
        model = Event
        fields = ['title','calendar',]
        widgets = {
            'calendar': forms.HiddenInput(),
        }