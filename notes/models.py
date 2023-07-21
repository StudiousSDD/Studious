from django.db import models
from datetime import date
from django.utils import timezone

# Create your models here.
class Event(models.Model):
    name_text = models.CharField(max_length=200)
    start_date = models.DateField(default=date.today);
    end_date = models.DateField(default=date.today);
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
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',) # Order by title alphabetically 

    def __str__(self):
        return self.meeting.__str__() + " " + self.note_title