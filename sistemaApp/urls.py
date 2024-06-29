
from . import views
from django.contrib import admin
from django.urls import path,include
app_name = 'sistemaApp'

urlpatterns = [
    path('crear_orden_compra/<int:articulo_id>/', views.crear_orden_compra, name='crear_orden_compra'),
    path('marcar_orden_recibida/<int:orden_compra_id>/', views.marcar_orden_recibida, name='marcar_orden_recibida'),
    path('predecir_demanda/<int:articulo_id>/', views.predecir_demanda_view, name='predecir_demanda_view'),
    path('cgi/<int:articulo_id>/', views.cgi_view, name='cgi'),
]