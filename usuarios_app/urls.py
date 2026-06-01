from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import Crear, Lista, Detalles, Actualizar, Eliminar, ImprimirPDF, ImprimePDF, ExportarView
from django.conf.urls.static import static
from django.conf import settings
from . import views
from .views import get_user_photo

urlpatterns = [
    path('api/user-photo/<int:user_id>/', get_user_photo, name='get_user_photo'),
]

urlpatterns = [
    path('crear/', Crear.as_view(), name='crear'),
    path('lista/', Lista.as_view(), name='listar_usuarios'),
    path('lista/detalles/<int:pk>', Detalles.as_view(), name='detalles'),
    path('lista/actualizar/<int:pk>', Actualizar.as_view(), name='actualizar'),
    path('lista/eliminar/<int:pk>', Eliminar.as_view(), name='eliminar'),
    path('lista/imprime/<int:pk>', ImprimePDF.as_view(), name='imprime'),
    path('lista/imprimir/', ImprimirPDF.as_view(), name='imprimir'),
    path('exportar/', ExportarView.as_view(), name='exportar'),

    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/create/', views.profile_create, name='profile_create'),
    path('profiles/update/<int:pk>/', views.profile_update, name='profile_update'),
    path('profiles/delete/<int:pk>/', views.profile_delete, name='profile_delete'),
    path('profiles/user-photo/<int:user_id>/', get_user_photo, name='get_user_photo'),
]
