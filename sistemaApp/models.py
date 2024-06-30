from django.db import models
from django.utils import timezone
from django.contrib import admin
from datetime import datetime

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
        
class Proveedor (models.Model):
    nombreProveedor = models.CharField(max_length=100,unique=True)
    fechaHoraBajaP = models.DateTimeField(default=None,null= True, blank=True) 
    demoraPedido = models.IntegerField(default=0,null= True, blank=True)
    costoPorPedido = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.nombreProveedor}"
    
class Articulo (models.Model):
    nombreArticulo = models.CharField(max_length=100,unique=True)
    stockActual = models.IntegerField(default=0)
    stockSeguridad = models.IntegerField(default=0)
    puntoPedido = models.IntegerField(default=0)
    precioArticulo = models.IntegerField(default=0)
    costoAlmacenamiento = models.IntegerField(default=0)
    loteOptimo = models.IntegerField(default=0)
    tiempoEntrePedidos = models.IntegerField(default=0)
    numeroPedidos = models.IntegerField(default=0)
    demandaPredecida = models.IntegerField(default=0)
    
    familiaArticulo = models.ForeignKey(FamiliaArticulo, on_delete=models.PROTECT,null=True, default=None)
    proveedor_predefinido = models.ForeignKey(Proveedor, on_delete=models.SET_NULL,null=True, default=None)
    
    def __str__(self):
        return f"{self.nombreArticulo}"
    
class EstadoOrdenCompra (models.Model):
    nombreEOC = models.CharField(max_length=100,unique=True)
    fechaHoraBajaEOC = models.DateTimeField(default=None,null= True, blank=True) 
    
    def __str__(self):
        return f"{self.nombreEOC}"
    
     
class OrdenCompra (models.Model):
    cantidadLote = models.IntegerField(default=1)
    montoTotal = models.IntegerField(default=0)
    estadoOrdenCompra = models.ForeignKey(EstadoOrdenCompra, on_delete=models.PROTECT)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='ordenes_compra')  #related_name se usa para establecer el nombre de la relación inversa desde articulo hacia OrdenCompra
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)

class OrdenVenta (models.Model):
    cantidadVendida = models.IntegerField(default=1)
    montoTotal = models.IntegerField(default=0)
    fechaHoraVenta = models.DateField(default=None,null= True, blank=True) 
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='ordenes_venta')  #related_name se usa para establecer el nombre de la relación inversa desde articulo hacia OrdenVenta
    
class DemandaHistorica(models.Model):
    MESES_CHOICES = (
        (1, 'Enero'),
        (2, 'Febrero'),
        (3, 'Marzo'),
        (4, 'Abril'),
        (5, 'Mayo'),
        (6, 'Junio'),
        (7, 'Julio'),
        (8, 'Agosto'),
        (9, 'Septiembre'),
        (10, 'Octubre'),
        (11, 'Noviembre'),
        (12, 'Diciembre'),
    )
    YEAR_CHOICES = [(year, str(year)) for year in range(1990, 2051)]
    mes = models.IntegerField(choices=MESES_CHOICES)
    año = models.IntegerField(choices=YEAR_CHOICES)
    cantidadDemanda = models.IntegerField(default=0)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='demandas_historicas')
    def __str__(self):
        return f'Demanda histórica: {self.get_mes_display()} {self.año}'
    
#CLASES AUXILIARES
class Accione(models.Model):
    mes = models.IntegerField()
    
#Enumeracion para el tipo error prediccion
class ErrorType(models.TextChoices):
    MAD = 'Desviación Absoluta Media'
    MSE = 'Error Cuadrado Medio'
    MAPE = 'Error Porcentual Absoluto Medio'