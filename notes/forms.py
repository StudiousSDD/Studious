from django.forms import ModelForm
from django import forms
from .models import Class 
from schedule.models.events import Event 

class AddClass(ModelForm):
    name = forms.TextInput()
    class Meta:
        model = Class
        fields = ['name']

class AddEvent(ModelForm):
    title = forms.TextInput()
    start = forms.TextInput()
    end = forms.TextInput()
    calendar = forms.TextInput() 
    class Meta: 
        model = Event
        fields = ['title','start','end','calendar']