from django.contrib import admin 
from django.urls import path
from . import views

# from notes.views import editor, delete_document, delete_class, view_class

app_name = "notes"
urlpatterns = [
    path("", views.home_calendar_view, name="home_page"),
    path("class/<int:classid>/delete", views.delete_class, name="delete_class"),
    path('delete_document/<int:noteid>/', views.delete_document, name='delete_document'),
    path('notes/', views.editor, name='editor'),
    path('add_class/', views.add_class, name='add_class'),
    path('add_event/', views.add_event, name='add_event'),
    path('class/<str:classname>/', views.view_class, name='view_class'),
]