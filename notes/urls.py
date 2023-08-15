from django.urls import path
from . import views

app_name = "notes"
urlpatterns = [
    # Calendar

    path("", views.home_calendar_view, name="home_page"),

    path('eventapi', views.occurrence_api, name="eventapi"),
    path('todoapi', views.todo_api, name="todoapi"),


    # Classes

    path('class/<int:classid>/', views.view_class, name='view_class'),
    path('class/event/<int:eventid>/', views.class_from_event, name='view_class_from_event'),

    path("class/<int:classid>/edit_class", views.edit_class, name="edit_class"),

    path('import_class/', views.import_class, name='import_class'),

    path("archive_class/<int:classid>/", views.archive_class, name="archive_class"),
    path("restore_class/<int:classid>/", views.restore_class, name="restore_class"),
    path("delete_class/<int:classid>/", views.delete_class, name="delete_class"),


    # Events

    path('add_event/', views.add_event, name='add_event'),


    # lectures

    path('create_lecture/', views.create_lecture, name='create_lecture'),


    # Notes

    path('notes/<int:lectureid>', views.editor, name='editor'),

    path('archive_document/<int:noteid>/', views.archive_document, name='archive_document'),
    path('delete_archived_note/<int:noteid>/', views.delete_archived_note, name='delete_archived_note'),
    path('restore_archived_note/<int:noteid>/', views.restore_archived_note, name='restore_archived_note'),
    
    path('notes/<int:lectureid>/<int:noteid>/outline', views.outline_view, name='outline'),

    
    # ToDos

    path('todo/<int:classid>', views.edit_todo, name="edit_todo"),
    path('todo/', views.edit_todo_no_class, name="edit_todo_no_class"),
    
    path('delete_todo/<int:todoid>', views.delete_todo, name='delete_todo'),
]