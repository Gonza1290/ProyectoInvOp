from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Articulo, EstadoOrdenCompra, OrdenCompra, OrdenVenta
#Signals se utiliza para definir y conectar funciones que deben ejecutarse en respuesta a ciertas señales de Django

# Definir estados de orden de compra
def inicializar_estados(sender, **kwargs):
    estados = ['Pendiente', 'Enviada', 'Recibido', 'Cancelada']
    for estado in estados:
        EstadoOrdenCompra.objects.get_or_create(nombreEOC=estado)

# Definir grupos y permisos
def create_groups_and_permissions(sender, **kwargs):
    # Crear grupos
    vendedor_group, created = Group.objects.get_or_create(name='Vendedor')
    gerente_group, created = Group.objects.get_or_create(name='Gerente')

    # Obtener el tipo de contenido para los modelos relevantes
    articulo_ct = ContentType.objects.get_for_model(Articulo)
    orden_compra_ct = ContentType.objects.get_for_model(OrdenCompra)
    orden_venta_ct = ContentType.objects.get_for_model(OrdenVenta)

    # Crear permisos
    can_view_articulo = Permission.objects.get(codename='view_articulo', content_type=articulo_ct)
    can_add_orden_compra = Permission.objects.get(codename='add_ordencompra', content_type=orden_compra_ct)
    can_change_orden_compra = Permission.objects.get(codename='change_ordencompra', content_type=orden_compra_ct)
    can_delete_orden_compra = Permission.objects.get(codename='delete_ordencompra', content_type=orden_compra_ct)
    can_add_orden_venta = Permission.objects.get(codename='add_ordenventa', content_type=orden_venta_ct)
    can_change_orden_venta = Permission.objects.get(codename='change_ordenventa', content_type=orden_venta_ct)
    can_delete_orden_venta = Permission.objects.get(codename='delete_ordenventa', content_type=orden_venta_ct)

    # Asignar permisos a grupos
    vendedor_group.permissions.set([can_view_articulo, can_add_orden_venta])
    gerente_group.permissions.set([can_view_articulo, can_add_orden_compra, can_change_orden_compra, can_delete_orden_compra, can_add_orden_venta, can_change_orden_venta, can_delete_orden_venta])