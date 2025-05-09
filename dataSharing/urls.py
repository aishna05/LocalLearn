from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download/', views.download_data, name='download'),
    path('upload/', views.upload_data, name='upload'),
]
