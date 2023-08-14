from django.db import models
from datetime import date
from django.utils import timezone
from ckeditor.widgets import CKEditorWidget

from schedule.models.events import Event, Occurrence


# Create your models here.

# to represent and manage tags 
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
        
# a Class needs an Event to show up on the calendar
# a Class has a name and the date it was created
# it is ordered alphabetically by name
# it is displayed as it's name
class Class(models.Model):
    calendar_event = models.OneToOneField(Event, on_delete=models.CASCADE, null=True)

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=('name',)   #   Order by class name alphabetically? 
        
    def __str__(self):
        return self.name
    
class ArchivedClass(models.Model):
    calendar_event = models.OneToOneField(Event, on_delete=models.CASCADE, null=True)

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    archived_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=('name',)   #   Order by class name alphabetically? 
        
    def __str__(self):
        return self.name

# a Lecture needs an Occurence as it represents a single Class time
# a Lecture is associated with a Class, each Class can have many Lectures
# a Lecture has no name and is instead numbered
# it is displayed as 'Class name' Lecture #'lecture_number' i.e. SD&D Lecture 1
class Lecture(models.Model):
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE, null=True)
    cls = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    lecture_number = models.IntegerField(default=0)
    def __str__(self):
        title = " Lecture #{}"
        return self.cls.__str__() + title.format(self.lecture_number)
    
# a Note is assocciated with a Lecture, each Leture can have many Notes
# A Note has a title, the text held within it, and dates of creation and modification
# their natural sorting is alphabetical by title
# a Note displays as 'Lecture display' 'Note title' i.e. SD&D Lecture 1 First Day Notes
class Note(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, null=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True)
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    color = models.CharField(max_length=255)

    class Meta:
        ordering = ('title',) # Order by title alphabetically 

    def __str__(self):
        return self.lecture.__str__() + " " + self.title

# an ArchivedNote is a way to hold the important information of a Note
# it is held separately to be restored or deleted later
class ArchivedNote(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, null=True)
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    archived_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title.__str__() 

# a to-do item is associated with a class
# it has a title, duedate, description and completed boolean value
class ToDo(models.Model):
    cls = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)

    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField(null=True)
    completed = models.BooleanField()
    def __str__(self) -> str:
        return self.title