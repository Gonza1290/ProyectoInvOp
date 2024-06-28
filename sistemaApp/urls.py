
from . import views
from django.contrib import admin
from django.urls import path,include
app_name = 'sistemaApp'

urlpatterns = [
    path('admin/crear_orden_compra/<int:articulo_id>/', views.crear_orden_compra, name='crear_orden_compra'),
    path('admin/marcar_orden_recibida/<int:orden_compra_id>/', views.marcar_orden_recibida, name='marcar_orden_recibida'),
    path('admin/predecir_demanda/<int:articulo_id>/', views.predecir_demanda_view, name='predecir_demanda_view'),
    path('admin/cgi/<int:articulo_id>/', views.crear_orden_compra, name='cgi'),
]