from django.db import models
from datetime import date
from django.utils import timezone
from ckeditor.widgets import CKEditorWidget

from schedule.models.events import Event, Occurrence

# Create your models here.
    
class Class(models.Model):
    calendar_event = models.OneToOneField(Event, on_delete=models.CASCADE, null=True)

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=('name',)   #   Order by class name alphabetically? 
        
    def __str__(self):
        return self.name

class Lecture(models.Model):
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE, null=True)
    event = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)

    meeting_number = models.IntegerField(default=0)
    def __str__(self):
        title = " Meeting #{}"
        return self.event.__str__() + title.format(self.meeting_number)
    

class Note(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, null=True)
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',) # Order by title alphabetically 

    def __str__(self):
        return self.lecture.__str__() + " " + self.title

class ArchivedNote(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, null=True)
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    archived_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title.__str__() 