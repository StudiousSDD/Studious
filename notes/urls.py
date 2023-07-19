from django.contrib import admin 
from django.urls import path
from . import views

from notes.views import editor, delete_document

app_name = "notes"
urlpatterns = [
    path("", views.home_calendar_view, name="home_page"),
    path("classes/", views.view_classes, name="view_classes"),
    path("delete_document/<int:noteid>/", views.delete_document, name="delete_document"),
]