from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.get_users, name='get_all_users'),
    path('user/<str:nick>', views.get_by_nick),
    path('data/', views.user_manager),
    path('register/', views.register_user),
    path('api/modelo/upload/', views.upload_modelo, name='upload_modelo'),
    path('upload-video/', views.upload_video, name='upload-video'),
    path('videos/resultados/', views.listar_todos_resultados, name='listar_todos_resultados'),
]
