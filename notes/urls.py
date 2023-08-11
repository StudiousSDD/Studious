from django.contrib import admin 
from django.urls import path
from . import views

# from notes.views import editor, delete_document, delete_class, view_class

app_name = "notes"
urlpatterns = [
    path("", views.home_calendar_view, name="home_page"),
    path("class/<int:classid>/delete", views.delete_class, name="delete_class"),
    path("class/<int:classid>/edit", views.edit_class, name="edit_class"),
    path('archive_document/<int:noteid>/', views.archive_document, name='archive_document'),

    path('eventapi', views.occurrence_api, name="eventapi"),

    path('import_class/', views.import_class, name='import_class'),
    path('notes/<int:lectureid>', views.editor, name='editor'),
    path('update_note_color/', views.update_note_color, name='update_note_color'),
    path('delete_archived_note/<int:noteid>/', views.delete_archived_note, name='delete_archived_note'),
    path('restore_archived_note/<int:noteid>/', views.restore_archived_note, name='restore_archived_note'),
    path('notes/<int:lectureid>/<int:noteid>/outline', views.outline_view, name='outline'),

    path('add_class/', views.add_class, name='add_class'),
    path('add_event/', views.add_event, name='add_event'),
    path('class/<str:classid>/', views.view_class, name='view_class'),

    path('create_lecture/', views.create_lecture, name='create_lecture'),

    path('todo/<int:classid>', views.edit_todo, name="edit_todo"),
]