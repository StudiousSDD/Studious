from django.db import models
from django.contrib.auth.models import User

from schedule.models.calendars import Calendar

# Create your models here.

# class ProfileManager(models.Manager):
#     def create_profile(self, user, calendar):
#         book = self.create(user=user, calendar=calendar)
#         # do something with the book
#         return book

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    calendar = models.OneToOneField(Calendar, on_delete=models.CASCADE)