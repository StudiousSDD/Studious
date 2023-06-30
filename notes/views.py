from django.shortcuts import render

# Create your views here.

def home_calendar_view(request):
    return render(request, "notes/calendar.html")

def view_classes(request):
    return render(request, "notes/view-classes.html")