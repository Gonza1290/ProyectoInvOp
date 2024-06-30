from django.contrib import admin
from .models import Articulo,FamiliaArticulo,ModeloInventario,EstadoOrdenCompra,OrdenCompra,Proveedor,DemandaHistorica,Accione,OrdenVenta
from django.db.models import F  # Agregar la importación de F
from django.db.models import Exists, OuterRef
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import redirect


class FamiliaArticuloAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_familia', 'modeloInventario', 'fechaHoraBajaFA')
    search_fields = ('id','nombreFamiliaArticulo')
    ordering = ('id',)
    list_display_links = ('nombre_familia',)
    
    
    #Metodo para mostrar otro nombre distinto del atributo
    def nombre_familia(self, obj):
        return obj.nombreFamiliaArticulo
    nombre_familia.short_description = 'Nombre de la Familia'
    
    # Action para dar de baja logica a FA
    def Eliminacion_Logica(modeladmin, request, queryset):
        for articulo in queryset:
            articulo.dar_de_baja()
    Eliminacion_Logica.short_description = "Eliminacion Logica"
    
    # Action para dar de baja logica a FA
    def Activacion_Logica(modeladmin, request, queryset):
        for articulo in queryset:
            articulo.dar_de_alta()
    Activacion_Logica.short_description = "Activacion Logica"
    
    #Agrego accion
    actions = [Eliminacion_Logica,Activacion_Logica]
    
#Clase que define un filtro personalizado en articulos
class ArticuloFaltanteFilter(admin.SimpleListFilter):
    title = 'Estado de Stock'  # Título del filtro que aparecerá en la interfaz de administración
    parameter_name = 'estado_stock'  # Nombre del parámetro de URL para este filtro

    def lookups(self, request, model_admin):
        # Define las opciones del filtro
        return (
            ('faltantes', 'Artículos faltantes'),  # Opción para artículos con stockActual < stockSeguridad
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
    list_display = ('id', 'nombreArticulo', 'stockActual','stockSeguridad','puntoPedido','precioArticulo','costoAlmacenamiento','loteOptimo','tiempoEntrePedidos','numeroPedidos','demandaPredecida','familiaArticulo','proveedor_predefinido')
    search_fields = ('id','nombreArticulo')
    ordering = ('id',)
    list_display_links = ('nombreArticulo',)
    list_filter = (ArticuloFaltanteFilter,)  # Agregar el filtro por stockActual

class EstadoOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreEOC', 'fechaHoraBajaEOC')
    ordering = ('id',)
    list_display_links = ('nombreEOC',)
    
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreProveedor', 'fechaHoraBajaP','demoraPedido','costoPorPedido')
    ordering = ('id',)
    list_display_links = ('nombreProveedor',)
         
class DemandaHistoricaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mes', 'año','cantidadDemanda','articulo')
    ordering = ('id',)
    
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'articulo', 'cantidadLote','montoTotal','estadoOrdenCompra','proveedor')
    ordering = ('estadoOrdenCompra',)

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
        acciones_html = ''
        estado_orden_compra= obj.estadoOrdenCompra
        if estado_orden_compra.nombreEOC == 'Pendiente':
            acciones_html += '<a class="btn btn-primary btn-sm" href="{}">Enviar Orden Compra</a>&nbsp;&nbsp;'.format(
                reverse('sistemaApp:enviar_orden_compra', args=[obj.id])
            )
        else:
            acciones_html += '<a class="btn btn-primary btn-sm" href="{}">Marcar como recibido</a>&nbsp;&nbsp;'.format(
                reverse('sistemaApp:marcar_orden_recibida', args=[obj.id])
            )
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
            reverse('sistemaApp:predecir_demanda_view', args=[obj.id])
        )
        acciones_html += '<a class="btn btn-warning btn-sm" href="{}">CGI</a>'.format(
            reverse('sistemaApp:cgi', args=[obj.id])
        )
        return format_html(acciones_html)
    
    def nombreArticulo(self, obj):
        return obj.nombreArticulos
    nombreArticulo.short_description = 'Nombre Articulo'
    
    def stockActual(self, obj):
        return obj.stockActual
    stockActual.short_description = 'Stock Actual'
    
    def puntoPedido(self, obj):
        return obj.puntoPedido
    puntoPedido.short_description = 'Punto Pedido'
    
    def has_add_permission(self, request):
        # Devuelve False para deshabilitar la opción de añadir nuevos registros
        return False

    def has_delete_permission(self, request, obj=None):
        # Devuelve False para deshabilitar la opción de eliminar registros
        return False
    
    def has_change_permission(self, request, obj=None):
        # Devuelve False para deshabilitar la opción de modificar instancias existentes
        return False

    
admin.site.register(FamiliaArticulo,FamiliaArticuloAdmin)
#@admin.register(FamiliaArticulo)
admin.site.register(Articulo,ArticuloAdmin)
admin.site.register(ModeloInventario)
admin.site.register(EstadoOrdenCompra,EstadoOrdenCompraAdmin)
admin.site.register(OrdenCompra,OrdenCompraAdmin)
admin.site.register(Proveedor,ProveedorAdmin)
admin.site.register(DemandaHistorica,DemandaHistoricaAdmin)
admin.site.register(Accione,AccionesAdmin)
admin.site.register(OrdenVenta,OrdenVentaAdmin)






