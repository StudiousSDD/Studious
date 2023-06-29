from django.urls import path

from . import views

app_name = "dispatch"
urlpatterns = [
    path("", views.home_calendar_view, name="home_page"),
]