from django.contrib import admin

# Register your models here.
from .models import Event, Meeting, Note, Class

admin.site.register(Event)
admin.site.register(Meeting)
admin.site.register(Note)
admin.site.register(Class)