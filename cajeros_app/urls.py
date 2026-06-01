from django.urls import path
from terceros_app.views import buscar_tercero
from .views import CajeroListView,CajeroCreateView,CajeroUpdateView,CajeroDeleteView

urlpatterns = [
    path('lista/',CajeroListView.as_view(), name='cajeros_list'),
    path('nuevo/',CajeroCreateView.as_view(), name='cajeros_create'),
    path('<int:pk>/editar/', CajeroUpdateView.as_view(), name='cajeros_update'),
    path('<int:pk>/eliminar/', CajeroDeleteView.as_view(), name='cajeros_delete'),
    path('buscar_tercero/<str:doc_ide>/', buscar_tercero, name='buscar_tercero'),
]
