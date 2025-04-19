from django.urls import path
from LL import views

urlpatterns = [
    path('service-worker.js', views.service_worker, name='service_worker'),
    path('signup/', views.signup, name='signup'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_subject/', views.add_subject, name='add_subject'),
    path('add_notes/', views.add_note, name='add_note'),
    path('edit_note/<int:note_id>/', views.edit_note, name='edit_note'),
    path('delete_note/<int:note_id>/', views.delete_note, name='delete_note'),
    path('delete_subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('delete_media/<int:media_id>/', views.delete_media, name='delete_media'),
    path('view_media/<int:media_id>/', views.view_media, name='view_media'),
    path('edit_media/<int:media_id>/', views.edit_media, name='edit_media'),
    path('search_notes/', views.search_notes, name='search_notes'),
    path('search_subject/', views.search_subject, name='search_subject'),
    path('share_note/<int:note_id>/', views.share_note, name='share_note'),
    path('share_notes/', views.share_notes_list, name='share_notes_list'),
    path('shared_notes/', views.shared_notes, name='shared_notes'),
    path('export_notes/', views.export_notes, name='export_notes'),
    path('import_notes/', views.import_notes, name='import_notes'),
    path('note/<int:note_id>/', views.view_note, name='view_note'),
]