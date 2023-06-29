from django.shortcuts import render

# Create your views here.

def home_calendar_view(request):
    return render(request, "notes/calendar.html")