from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import CreditoCreateView,UpdateViewCredito,calculo_cuota_view,prueba_fecha,ImprimePlanAmortizacionPDF,CreditosListView
from .views import confirmar_eliminar_credito,agregar_codeudor,editar_codeudor,eliminar_codeudor, creditos_desembolsados
from creditos_app.view_liq_cre import liquidar_creditos,liquidacion_justo,consulta_detalle_prod

from django.conf.urls.static import static

urlpatterns = [
    path('lista/', CreditosListView.as_view(), name='creditos_list'),
    path('crear/',CreditoCreateView.as_view(), name='crear_credito_justo'),
    path('actualizar/<int:pk>/',UpdateViewCredito.as_view(), name='actualizar_credito'),
    path('calcuo_cuota/',calculo_cuota_view, name='calculo_cuota'),
    path('imprimir_plan_amort/',ImprimePlanAmortizacionPDF, name='imp_plan_amortizacion'),
    path('prueba-fecha/',prueba_fecha, name='prueba_fecha'),
    path('liquidar_creditos/',liquidar_creditos, name='liquidar_creditos'),
    path('liquidacion/<int:pk>/', liquidacion_justo, name='liquidacion_justo'),
    path('detalle-prod/<str:subcuenta>/',consulta_detalle_prod, name='consulta_detalle_prod'), 
    path('eliminar/<int:pk>/confirmar/',confirmar_eliminar_credito, name='confirmar_eliminar_credito'),
    path('codeudor/<int:credito_id>/agregar_codeudor/', agregar_codeudor, name='agregar_codeudor'),
    path('codeudor/<int:codeudor_id>/editar/', editar_codeudor, name='editar_codeudor'),
    path('codeudor/<int:codeudor_id>/eliminar/', eliminar_codeudor, name='eliminar_codeudor'),
    path('desembolsados/',creditos_desembolsados, name='creditos_desembolsados'),
]
