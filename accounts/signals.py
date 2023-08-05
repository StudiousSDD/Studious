from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from schedule.models.calendars import Calendar

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        calendar = Calendar.objects.create(name=instance.username, slug=instance.username)
        Profile.objects.create(user=instance, calendar=calendar)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
