from django.db import models
from datetime import date
from django.utils import timezone

from schedule.models.events import Event, Occurrence

# Create your models here.
    
class Class(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    # calendar_event = models.OneToOneField(Event, on_delete=models.CASCADE)

    class Meta:
        ordering=('name',)   #   Order by class name alphabetically? 
    def __str__(self):
        return self.name

class Lecture(models.Model):
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE, null=True)
    # instead of a FK to an Event, a meeting should probably have an FK
    # to an Occurance from the django-scheduler app. Occurrences are linked
    # to Scheduler Events in their backend. These are auto-generated when needed
    # from the django-scheduler Events as necessary. Once there is an FK to
    # one, I believe it will save it in the database long-term         
    # There will only be one Meeting per Occurrence, and then multiple Notes
    # can be tied to the single Meeting, I think would be easiest.      -Tom
    meeting_number = models.IntegerField(default=0)
    def __str__(self):
        title = " Meeting #{}"
        return self.event.__str__() + title.format(self.meeting_number)
    

class Note(models.Model):
    # meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    
    # A FK to a Meeting above (which is then connected to an Occurance) I think is
    # what we'd want here.              -Tom
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',) # Order by title alphabetically 

    def __str__(self):
        return self.meeting.__str__() + " " + self.note_title
