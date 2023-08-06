from django.contrib import admin

# Register your models here.
from .models import Lecture, Note, Class, ArchivedNote

admin.site.register(Lecture)
admin.site.register(Note)
admin.site.register(Class)
admin.site.register(ArchivedNote)