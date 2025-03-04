from django.contrib import admin, messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Exists, OuterRef
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from django.db import transaction
from sistemaApp.models import (
    Articulo,
    Categoria,
    SubCategoria,
    Marca,
    UnidadMedida,
    EstadoOrdenCompra,
    OrdenCompra,
    Proveedor,
    DemandaHistorica,
    Accione,
    OrdenVenta,
    ModeloInventario
)

from django.contrib import messages
from django.db import transaction

# Clase que permite agregar acciones personalizadas a los modelos de Django
class LogicalDeletionMixin:
    @transaction.atomic
    def Eliminacion_Logica(self, request, queryset):
        try:
            for obj in queryset:
                obj.dar_de_baja()
            self.message_user(request, "Eliminación lógica realizada con éxito.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error al realizar la eliminación lógica: {e}", messages.ERROR)
    Eliminacion_Logica.short_description = "Eliminación Lógica"

    @transaction.atomic
    def Activacion_Logica(self, request, queryset):
        try:
            for obj in queryset:
                obj.dar_de_alta()
            self.message_user(request, "Activación lógica realizada con éxito.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error al realizar la activación lógica: {e}", messages.ERROR)
    Activacion_Logica.short_description = "Activación Lógica"

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreCategoria', 'modeloInventario', 'fechaHoraBaja')
    search_fields = ('id','nombreCategoria')
    ordering = ('nombreCategoria',)
    list_display_links = ('nombreCategoria',)
    exclude = ('fechaHoraBaja',)
    actions = [LogicalDeletionMixin.Eliminacion_Logica, LogicalDeletionMixin.Activacion_Logica]

class SubCategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreSubCategoria', 'get_categories','fechaHoraBaja')
    search_fields = ('id','nombreSubCategoria')  
    ordering = ('nombreSubCategoria',)
    list_display_links = ('nombreSubCategoria',)
    exclude = ('fechaHoraBaja',)
    actions = [LogicalDeletionMixin.Eliminacion_Logica, LogicalDeletionMixin.Activacion_Logica]

class MarcaAdmin (admin.ModelAdmin):
    list_display = ('id', 'nombreMarca')
    search_fields = ('id','nombreMarca')
    ordering = ('nombreMarca',)
    list_display_links = ('nombreMarca',)
    exclude = ('fechaHoraBaja',)
    actions = [LogicalDeletionMixin.Eliminacion_Logica, LogicalDeletionMixin.Activacion_Logica]
    
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreUnidadMedida')
    search_fields = ('id','nombreUnidadMedida')
    ordering = ('nombreUnidadMedida',)
    list_display_links = ('nombreUnidadMedida',)
    exclude = ('fechaHoraBaja',)
    actions = [LogicalDeletionMixin.Eliminacion_Logica, LogicalDeletionMixin.Activacion_Logica]
    
#Clase que define un filtro personalizado en articulos
class ArticuloFaltanteFilter(admin.SimpleListFilter):
    title = 'Estado de Stock'  # Título del filtro que aparecerá en la interfaz de administración
    parameter_name = 'estado_stock'  # Nombre del parámetro de URL para este filtro

    def lookups(self, request, model_admin):
        # Define las opciones del filtro
        return (
            ('faltantes', 'Artículos Faltantes'),  # Opción para artículos con stockActual < stockSeguridad
            ('reponer', 'Articulos a Reponer'),  # Opción para artículos con stockActual < puntoPedido
        )

    #queryset inicialmente tienen todos los articulos existentes
    def queryset(self, request, queryset):
        if self.value() == 'faltantes':
            return queryset.filter(stockActual__lt=F('stockSeguridad'))
        elif self.value() == 'reponer':
            subquery = OrdenCompra.objects.filter(  #subquery es una subconsulta
                articulo_id=OuterRef('pk'),
                estadoOrdenCompra__nombreEOC='Pendiente'
            )
            return queryset.annotate(               #annotate agrega un campo adicional a todos los articulos
                tiene_orden_pendiente=Exists(subquery)
            ).filter(
                stockActual__lt=F('puntoPedido'),
                tiene_orden_pendiente=False
            )
        
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreArticulo', 'stockActual','stockSeguridad','puntoPedido','precioArticulo','loteOptimo','categoria','proveedor_predefinido','marca','fechaHoraBaja')
    search_fields = ('id','nombreArticulo')
    ordering = ('id',)
    list_display_links = ('nombreArticulo',)
    list_filter = (ArticuloFaltanteFilter,)  # Agregar el filtro por stockActual
    exclude = ('fechaHoraBaja','tiempoEntrePedidos','numeroPedidos','demandaPredecida',)  # Excluir el campo fechaHoraBaja del formulario
    actions = [LogicalDeletionMixin.Eliminacion_Logica, LogicalDeletionMixin.Activacion_Logica]

class EstadoOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreEOC', 'fechaHoraBaja')
    ordering = ('id',)
    list_display_links = ('nombreEOC',)
    exclude = ('fechaHoraBaja',)
    actions = [LogicalDeletionMixin.Eliminacion_Logica, LogicalDeletionMixin.Activacion_Logica]
    
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreProveedor', 'fechaHoraBaja','demoraPedido','costoPorPedido')
    ordering = ('id',)
    list_display_links = ('nombreProveedor',)
    exclude = ('fechaHoraBaja',)
    actions = [LogicalDeletionMixin.Eliminacion_Logica, LogicalDeletionMixin.Activacion_Logica]
         
class DemandaHistoricaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mes', 'año','cantidadDemanda','articulo')
    ordering = ('mes','año',)
    
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'articulo', 'fechaHoraCompra','cantidadLote','montoTotal','estadoOrdenCompra','proveedor')
    ordering = ('estadoOrdenCompra__nombreEOC',)

    def estadoOrdenCompra(self):
        return self.nombreCategoria
    estadoOrdenCompra.short_description = 'Estado Orden Compra'
    
    def has_add_permission(self, request):
        # Devuelve False para deshabilitar la opción de añadir nuevos registros
        return False
    
    def has_change_permission(self, request, obj=None):
        # Devuelve False para deshabilitar la opción de modificar instancias existentes
        return False
    
    def get_list_display(self, request):
        # Obtener la lista de campos a mostrar
        list_display = super().get_list_display(request)
        # Agregar el botón personalizado a la lista de campos a mostrar
        list_display += ('Acciones',)
        return list_display

    def Acciones(self, obj):
        estado_orden_compra = obj.estadoOrdenCompra.nombreEOC
        acciones = {
            'Pendiente': (
                '<a class="btn btn-primary btn-sm" href="{}">Enviar Orden Compra</a>&nbsp;&nbsp;'.format(
                    reverse('sistemaApp:enviar_orden_compra', args=[obj.id])
                ) +
                '<a class="btn btn-danger btn-sm" href="{}">Cancelar Orden Compra</a>&nbsp;&nbsp;'.format(
                    reverse('sistemaApp:cancelar_orden_compra', args=[obj.id])
                )
            ),
            'Enviada': (
                '<a class="btn btn-primary btn-sm" href="{}">Marcar como recibido</a>&nbsp;&nbsp;'.format(
                    reverse('sistemaApp:marcar_orden_recibida', args=[obj.id])
                )
            ),
            'Recibido': (
                '<span class="btn btn-secondary btn-sm disabled">Recibido</span>&nbsp;&nbsp;'
            ),
            'Cancelada': (
                '<span class="btn btn-secondary btn-sm disabled">Cancelada</span>&nbsp;&nbsp;'
            )
        }

        acciones_html = acciones.get(estado_orden_compra, '')
        return format_html(acciones_html)

class OrdenVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'articulo', 'fechaHoraVenta','cantidadVendida','montoTotal')
    ordering = ('fechaHoraVenta',)

    def has_add_permission(self, request):
        # Devuelve False para deshabilitar la opción de añadir nuevos registros
        return False
    
    def has_change_permission(self, request, obj=None):
        # Devuelve False para deshabilitar la opción de modificar instancias existentes
        return False
    
class AccionesAdmin(admin.ModelAdmin):
    list_display_links = None

    def get_queryset(self, request):
        # Obtener el queryset estándar de todos los objetos de Articulo
        return Articulo.objects.all()

    def get_list_display(self, request):
        # Obtener la lista de campos a mostrar
        list_display = super().get_list_display(request)
        # Agregar el botón personalizado a la lista de campos a mostrar
        list_display = ('nombreArticulo','stockActual','puntoPedido','Acciones',)
        return list_display

    def Acciones(self, obj):
        acciones_html = ''
        acciones_html += '<a class="btn btn-primary btn-sm" href="{}">Crear Orden de Compra</a>&nbsp;&nbsp;'.format(
            reverse('sistemaApp:crear_orden_compra', args=[obj.id])
        )
        acciones_html += '<a class="btn btn-primary btn-sm" href="{}">Crear Orden de Venta</a>&nbsp;&nbsp;'.format(
            reverse('sistemaApp:crear_orden_venta', args=[obj.id])
        )
        acciones_html += '<a class="btn btn-info btn-sm" href="{}">Predecir Demanda</a>&nbsp;&nbsp;'.format(
            reverse('sistemaApp:predecir_demanda', args=[obj.id])
        )
        acciones_html += '<a class="btn btn-warning btn-sm" href="{}">CGI</a>'.format(
            reverse('sistemaApp:cgi', args=[obj.id])
        )
        return format_html(acciones_html)
    
    def has_add_permission(self, request):
        # Devuelve False para deshabilitar la opción de añadir nuevos registros
        return False

    def has_delete_permission(self, request, obj=None):
        # Devuelve False para deshabilitar la opción de eliminar registros
        return False
    
    def has_change_permission(self, request, obj=None):
        # Devuelve False para deshabilitar la opción de modificar instancias existentes
        return False

class ModeloInventarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreMI', 'fechaHoraBaja')
    search_fields = ('id','nombreMI')
    ordering = ('id',)
    list_display_links = ('nombreMI',)
    exclude = ('fechaHoraBaja',)
    actions = [LogicalDeletionMixin.Eliminacion_Logica, LogicalDeletionMixin.Activacion_Logica]
    
admin.site.register(Categoria,CategoriaAdmin)
admin.site.register(SubCategoria,SubCategoriaAdmin)
admin.site.register(Marca,MarcaAdmin)
admin.site.register(UnidadMedida,UnidadMedidaAdmin)
admin.site.register(Articulo,ArticuloAdmin)
admin.site.register(ModeloInventario, ModeloInventarioAdmin)
admin.site.register(EstadoOrdenCompra,EstadoOrdenCompraAdmin)
admin.site.register(OrdenCompra,OrdenCompraAdmin)
admin.site.register(Proveedor,ProveedorAdmin)
admin.site.register(DemandaHistorica,DemandaHistoricaAdmin)
admin.site.register(Accione,AccionesAdmin)
admin.site.register(OrdenVenta,OrdenVentaAdmin)


