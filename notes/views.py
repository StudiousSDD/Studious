from django.shortcuts import render

from .models import Note
# Create your views here.

def editor(request):
    noteid = int(request.GET.get('noteid',0))
    note = Note.objects.all()

    context = {
        'noteid' : noteid,
        'note' : note
    }
    return render(request, 'notes/editor.html',context)                 

def home_calendar_view(request):
    return render(request, "notes/calendar.html")

def view_classes(request):
    return render(request, "notes/view-classes.html")