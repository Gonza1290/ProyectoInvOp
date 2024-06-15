from django.contrib import admin
from .models import Articulo,FamiliaArticulo,ModeloInventario,EstadoOrdenCompra,OrdenCompra,Proveedor,DemandaHistorica
from django.db.models import F  # Agregar la importación de F
from django.db.models import Exists, OuterRef

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
    list_display = ('id', 'nombreArticulo', 'stockActual','stockSeguridad','puntoPedido','precioArticulo','costoAlmacenamiento','familiaArticulo')
    search_fields = ('id','nombreArticulo')
    ordering = ('id',)
    list_display_links = ('nombreArticulo',)
    list_filter = (ArticuloFaltanteFilter,)  # Agregar el filtro por stockActual

class EstadoOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreEOC', 'fechaHoraBajaEOC')
    ordering = ('id',)
    list_display_links = ('nombreEOC',)
    
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'cantidadLote', 'articulo','proveedor')
    ordering = ('id',)

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreProveedor', 'fechaHoraBajaP','demoraPedido','costoPorPedido')
    ordering = ('id',)
    list_display_links = ('nombreProveedor',)
         
class DemandaHistoricaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mes', 'año','cantidadDemanda')
    ordering = ('id',)

admin.site.register(FamiliaArticulo,FamiliaArticuloAdmin)
#@admin.register(FamiliaArticulo)
admin.site.register(Articulo,ArticuloAdmin)
admin.site.register(ModeloInventario)
admin.site.register(EstadoOrdenCompra,EstadoOrdenCompraAdmin)
admin.site.register(OrdenCompra,OrdenCompraAdmin)
admin.site.register(Proveedor,ProveedorAdmin)
admin.site.register(DemandaHistorica,DemandaHistoricaAdmin)








