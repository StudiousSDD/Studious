from django.db import models

# Create your models here.
class Event(models.Model):
    name_text = models.CharField(max_length=200)
    def __str__(self):
        return self.name_text


class Meeting(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    meeting_number = models.IntegerField(default=0)
    def __str__(self):
        title = "Meeting #{}"
        return title.format(self.meeting_number)

class Note(models.Model):
    # meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('title',) # Order by title alphabetically 

    def __str__(self):
        return self.title