from django.urls import path

from . import views

app_name = "notes"
urlpatterns = [
    path("", views.home_calendar_view, name="home_page"),
    path("classes/", views.view_classes, name="view_classes"),
]