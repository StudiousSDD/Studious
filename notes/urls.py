from django.contrib import admin 
from django.urls import path
from . import views

from notes.views import editor, delete_document, delete_class, view_classes

app_name = "notes"
urlpatterns = [
    path("", views.home_calendar_view, name="home_page"),
    path("classes/<int:classid>", delete_class, name="delete_class"),
    path('delete_document/<int:noteid>/', delete_document, name='delete_document'),
    path('add_class/',views.add_class, name='add_class'),
    path('classes/',view_classes,name='view_classes'),
]