from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Articulo, EstadoOrdenCompra, ModeloInventario
from django.dispatch import receiver
from django.db.models.signals import post_migrate
#Signals se utiliza para definir y conectar funciones que deben ejecutarse en respuesta a ciertas señales de Django
#Signals se importan y se usan en apps.py 

# Definir estados de orden de compra
@receiver(post_migrate) #post_migrate es una señal que se envía después de que se ha migrado la base de datos
def inicializar_estados(sender, **kwargs):
    estados = ['Pendiente', 'Enviada', 'Recibido', 'Cancelada']
    for estado in estados:
        EstadoOrdenCompra.objects.get_or_create(nombreEOC=estado)

# Definir grupos y permisos
@receiver(post_migrate)
def create_groups_and_permissions(sender, **kwargs):
    # Crear grupos
    vendedor_group, created = Group.objects.get_or_create(name='Vendedor')
    gerente_group, created = Group.objects.get_or_create(name='Gerente')

    # Obtener el tipo de contenido para los modelos relevantes
    content_types = ContentType.objects.filter(app_label='sistemaApp')

    # Crear permisos y asignarlos al grupo de Vendedores
    for content_type in content_types:
        permissions = Permission.objects.filter(content_type=content_type)
        for permission in permissions:
            vendedor_group.permissions.add(permission)

    # Guardar los cambios
    vendedor_group.save()
    gerente_group.save()


@receiver(post_migrate)
def create_modelo_inventario(sender, **kwargs):
    # Crear modelo de inventario
    modelo_lote_fijo, created = ModeloInventario.objects.get_or_create(nombreMI='Modelo Lote Fijo')
    modelo_intervalo_fijo, created = ModeloInventario.objects.get_or_create(nombreMI='Modelo Intervalo Fijo')

    