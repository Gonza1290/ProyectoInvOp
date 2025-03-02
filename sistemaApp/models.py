from django.db import models
from django.utils import timezone
from django.contrib import admin
from datetime import datetime

# Clase base para modelos con baja lógica
class BaseModel(models.Model):
    fechaHoraBaja = models.DateTimeField(default=None, null=True, blank=True) #Blank=True significa que el campo no es obligatorio en los formularios

    class Meta:
        abstract = True

    def dar_de_baja(self):
        self.fechaHoraBaja = timezone.now()
        self.save()

    def dar_de_alta(self):
        self.fechaHoraBaja = None
        self.save()

class ModeloInventario(BaseModel):
    nombreMI = models.CharField(max_length=100)
    descripcionMI = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.nombreMI}"

class SubCategoria(BaseModel):
    nombreSubCategoria = models.CharField(max_length=100, unique=True)
    categories = models.ManyToManyField('Categoria', related_name='subCategories', blank=True)

    def __str__(self):
        return f"{self.nombreSubCategoria}"
    
    def get_categories(self):
        return ", ".join([Categoria.nombreCategoria for Categoria in self.categories.all()])
    get_categories.short_description = 'Categories'

class Categoria(BaseModel):
    nombreCategoria= models.CharField(max_length=100, unique=True)
    modeloInventario = models.ForeignKey(ModeloInventario, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nombreCategoria}"

class Proveedor(BaseModel):
    nombreProveedor = models.CharField(max_length=100, unique=True)
    demoraPedido = models.IntegerField(default=0, null=True, blank=True)
    costoPorPedido = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombreProveedor}"

class Marca(BaseModel):
    nombreMarca = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.nombreMarca}"

class UnidadMedida(BaseModel):
    nombreUnidadMedida = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombreUnidadMedida}"

class EstadoOrdenCompra(BaseModel):
    nombreEOC = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.nombreEOC}"

class Articulo(BaseModel):
    nombreArticulo = models.CharField(max_length=100, unique=True)
    stockActual = models.IntegerField(default=0)
    stockSeguridad = models.IntegerField(default=0)
    puntoPedido = models.IntegerField(default=0, null=True, blank=True)
    precioArticulo = models.IntegerField(default=0)
    costoAlmacenamiento = models.IntegerField(default=0)
    loteOptimo = models.IntegerField(default=0)
    tiempoEntrePedidos = models.IntegerField(default=0, null=True, blank=True)
    numeroPedidos = models.IntegerField(default=0, null=True, blank=True)
    demandaPredecida = models.IntegerField(default=0, null=True, blank=True)
    descripcionArticulo = models.TextField(default=None, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, null=True, default=None)
    proveedor_predefinido = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, default=None)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, null=False)
    unidadMedida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, null=False)

    def __str__(self):
        return f"{self.nombreArticulo}"

    def nombre_articulo(self):
        return self.nombreArticulo

    nombre_articulo.short_description = 'Nombre del Artículo'

    def nombre_categoria(self):
        return self.Categoria.nombreCategoria

    nombre_categoria.short_description = 'Nombre de la Categoria'

    def nombre_proveedor(self):
        return self.proveedor_predefinido.nombreProveedor

    nombre_proveedor.short_description = 'Proveedor Predefinido'

class OrdenCompra(models.Model):
    cantidadLote = models.IntegerField(default=1)
    montoTotal = models.IntegerField(default=0)
    fechaHoraCompra = models.DateTimeField(auto_now_add=True) #auto_now_add=True significa que se establece la fecha y hora actual en el momento de la creación del objeto
    estadoOrdenCompra = models.ForeignKey(EstadoOrdenCompra, on_delete=models.PROTECT)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='ordenes_compra')  #related_name se usa para establecer el nombre de la relación inversa desde articulo hacia OrdenCompra
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.articulo.nombreArticulo}"

class OrdenVenta(models.Model):
    cantidadVendida = models.IntegerField(default=1)
    montoTotal = models.IntegerField(default=0)
    fechaHoraVenta = models.DateTimeField(auto_now_add=True)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='ordenes_venta')

    def __str__(self):
        return f"{self.articulo.nombreArticulo}"

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

# CLASES AUXILIARES
class Accione(models.Model):
    mes = models.IntegerField()

    def nombreArticulo(self):
        return self.nombreArticulos

    nombreArticulo.short_description = 'Nombre Articulo'

    def stockActual(self):
        return self.stockActual

    stockActual.short_description = 'Stock Actual'

    def puntoPedido(self):
        return self.puntoPedido

    puntoPedido.short_description = 'Punto Pedido'

# Enumeracion para el tipo error prediccion
class ErrorType(models.TextChoices):
    MAD = 'Desviación Absoluta Media'
    MSE = 'Error Cuadrado Medio'
    MAPE = 'Error Porcentual Absoluto Medio'