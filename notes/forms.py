from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Class, Note, Tag
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
# a form to get necessary data to create an event
class AddEvent(ModelForm):
    color_widget  = forms.TextInput(attrs={'type': 'range', 'min': 0, 'max': 359, 'step': 1, 'class': 'slider'})
    color = forms.IntegerField(min_value=0, max_value=359, widget=color_widget)
    
    time_widget = forms.TextInput(attrs={'type': 'time'})
    date_widget = forms.TextInput(attrs={'type': 'date'})
    
    start_time = forms.TimeField(widget=time_widget)
    end_time = forms.TimeField(widget=time_widget)

    start_date = forms.DateField(widget=date_widget)
    end_date = forms.DateField(widget=date_widget)
    
    repeat = forms.MultipleChoiceField(choices=days_of_week, widget=forms.CheckboxSelectMultiple())
    
    class Meta: 
        model = Event
        fields = ['title', 'calendar',]
        widgets = {
            'calendar': forms.HiddenInput(),
        }
        labels = {
            'end_recurring_period': _("End Repeat"),
        }
# a form to get a file
class ImportEvent(ModelForm):
    file = forms.FileField()
    class Meta:
        model = Event
        fields = ['calendar', 'file']
        widgets = {
            'calendar': forms.HiddenInput(),
        }
# a form to get event info allowed for editing
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
# allow users to select a tag or create a new tag for each note
class NoteForm(forms.ModelForm):
    new_tag = forms.CharField(max_length=100, required=False, label="Create New Tag", widget=forms.TextInput(attrs={'placeholder': 'e.g., homework'}))
    delete_tag = forms.BooleanField(required=False, label="Delete Tag")

    class Meta:
        model = Note
        fields = ['title', 'content', 'tag']

    def __init__(self, *args, **kwargs):
        username = kwargs.pop('username', None)
        super(NoteForm, self).__init__(*args, **kwargs)

        qset = Tag.objects.filter(user__username=username)
        self.fields["tag"] = forms.ModelChoiceField(queryset=qset, required=False, label="Select Tag")
        