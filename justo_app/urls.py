from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from . import views
from justo_app.views import dashboard, Registrar_Usuario, Iniciar_Sesion, Cerrar_Sesion, Restablecer_Contraseña, Resumen, Cuentas_Por_Pagar, Archivo_Plano, exportar_excel_resumen, exportar_pdf_resumen, cuentas_masivas
from django.conf.urls.static import static

urlpatterns = [
    path('keep-alive/', views.keep_alive, name='keep_alive'),
    # path('', views.Inicio, name= 'inicio'),
    path('', views.dashboard, name= 'inicio'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('Registrar_Usuario/', views.Registrar_Usuario, name='registrar_usuario'),
    path('Iniciar_Sesion/', views.Iniciar_Sesion, name='iniciar_sesion'),
    path('Cerrar_Sesion/', views.Cerrar_Sesion, name='cerrar_sesion'),
    path('Restablecer_Contraseña/', views.Restablecer_Contraseña, name='restablecer_contrasena'),
    path('Resumen/', views.Resumen, name='resumen'),
    path('Archivo_Plano/', views.Archivo_Plano, name='archivo_plano'),  
    path('cuenta_x_pagar/<int:trabajador_id>/', Cuentas_Por_Pagar, name='cuenta_por_pagar'),
    path('excel/', exportar_excel_resumen, name='exportar_excel_resumen'),
    path('pdf/', exportar_pdf_resumen, name='exportar_pdf_resumen'),
    path('cuentas_masivas/', cuentas_masivas, name='cuentas_masivas'),

]
