from django.db import models
from datetime import date
from django.utils import timezone

from schedule.models.events import Event

# Create your models here.
class Event(models.Model):
    name_text = models.CharField(max_length=200)
    # calendar_event will point to an event from the django-scheduler app 
    # which is what makes the calendar on the main screen populate      -Tom
    calendar_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    def __str__(self):
        return self.name_text
    
class Schedule(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    day = models.CharField(max_length=3)
    start_time = models.TimeField(default=timezone.now)
    duration = models.DurationField(default=0)
    def __str__(self):
        return self.event.__str__() + " on " + self.day


class Meeting(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    # instead of a FK to an Event, a meeting should probably have an FK
    # to an Occurance from the django-scheduler app. These are auto-generated
    # from the django-scheduler Events as necessary. Once there is an FK to
    # one, I believe it will save it in the database long-term          -Tom
    meeting_number = models.IntegerField(default=0)
    def __str__(self):
        title = " Meeting #{}"
        return self.event.__str__() + title.format(self.meeting_number)
    
class Class(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=('name',)   #   Order by class name alphabetically? 
    def __str__(self):
        return self.name

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