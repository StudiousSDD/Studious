from django.forms import ModelForm
from django import forms
from .models import Class 

class AddClass(ModelForm):
    name = forms.TextInput()
    class Meta:
        model = Class
        fields = ['name']