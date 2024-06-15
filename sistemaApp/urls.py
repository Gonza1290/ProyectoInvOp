
from . import views
from django.contrib import admin
from django.urls import path,include
app_name = 'sistemaApp'

urlpatterns = [
    path('admin/crear_orden_compra/<int:articulo_id>/', views.crear_orden_compra, name='crear_orden_compra'),
    path('admin/predecir_demanda/<int:articulo_id>/', views.crear_orden_compra, name='predecir_demanda'),
    path('admin/cgi/<int:articulo_id>/', views.crear_orden_compra, name='cgi'),
]