from django.db import models
from django.utils import timezone
from django.contrib import admin
# Create your models here.

class ModeloInventario (models.Model):
    nombreMI = models.CharField(max_length=100,unique=True)
    fechaHoraBajaMI = models.DateTimeField(default=None,null= True, blank=True) 
    
    def __str__(self):
        return f"{self.nombreMI}"
    
class FamiliaArticulo (models.Model):
    nombreFamiliaArticulo = models.CharField(max_length=100,unique=True)
    fechaHoraBajaFA = models.DateTimeField(default=None,null= True, blank=True)
    modeloInventario = models.ForeignKey(ModeloInventario, on_delete=models.PROTECT)
    
    def __str__(self):
        return f"{self.nombreFamiliaArticulo}"
    
    def dar_de_baja(self):
      self.fechaHoraBajaFA = timezone.now()
      self.save()
        
    def dar_de_alta(self):
        self.fechaHoraBajaFA = None
        self.save()
        
class Articulo (models.Model):
    nombreArticulo = models.CharField(max_length=100,unique=True)
    stockActual = models.IntegerField(default=0)
    stockSeguridad = models.IntegerField(default=0)
    puntoPedido = models.IntegerField(default=0)
    precioArticulo = models.IntegerField(default=0)
    costoAlmacenamiento = models.IntegerField(default=0)
    familiaArticulo = models.ForeignKey(FamiliaArticulo, on_delete=models.PROTECT,null=True, default=None)

    def __str__(self):
        return f"{self.nombreArticulo}"
    
class EstadoOrdenCompra (models.Model):
    nombreEOC = models.CharField(max_length=100,unique=True)
    fechaHoraBajaEOC = models.DateTimeField(default=None,null= True, blank=True) 
    
    def __str__(self):
        return f"{self.nombreEOC}"
    
class Proveedor (models.Model):
    nombreProveedor = models.CharField(max_length=100,unique=True)
    fechaHoraBajaP = models.DateTimeField(default=None,null= True, blank=True) 
    demoraPedido = models.IntegerField(default=0,null= True, blank=True)
    costoPorPedido = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.nombreProveedor}"
     
class OrdenCompra (models.Model):
    cantidadLote = models.IntegerField(default=1)
    estadoOrdenCompra = models.ForeignKey(EstadoOrdenCompra, on_delete=models.PROTECT)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='ordenes_compra')  #related_name se usa para establecer el nombre de la relación inversa desde articulo hacia OrdenCompra
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)

    

