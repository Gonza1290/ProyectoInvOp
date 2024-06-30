
# Proyecto InvOp

Descripción Técnica del Sistema de Inventarios

Introducción
El sistema de inventarios está diseñado para gestionar y optimizar el inventario de artículos utilizando métodos de predicción de demanda y modelos de gestión de inventarios. Este sistema permite realizar predicciones de demanda a través de métodos estadísticos como Promedio Móvil, Promedio Móvil Ponderado y Suavización Exponencial, y calcula el Costo de Gestión de Inventario (CGI) mediante los modelos de inventario por Lote Fijo e Intervalo Fijo. A continuación, se detallan los módulos principales del sistema y sus funcionalidades.

1. Modulo Maestro de Artículos
   
Alta tabla Artículos:
Coherencia en la codificación: El sistema garantiza que no haya duplicación de códigos de artículos, manteniendo la unicidad y consistencia de los datos.

Modificación de tabla Artículos: Permite realizar cambios en cascada, es decir, cualquier cambio en el código de un producto terminado (PT) se refleja automáticamente en las tablas relacionadas.

Baja tabla Artículos: Controla la baja de artículos, impidiendo la eliminación de artículos que tengan órdenes de compra pendientes o en curso.

Informes tabla Artículos:
Listado de Productos Terminados (Prod Term)

2. Modulo Inventario
   
Determinación del Modelo de Inventario por familia de artículo

Permite seleccionar el modelo de inventario adecuado para cada artículo, con posibilidad de modificar la selección posteriormente.

Calculo del Modelo Lote Fijo: Almacena datos necesarios para calcular el Lote Óptimo, Punto de Pedido y Stock de Seguridad para cada artículo que utilice este modelo.

Calculo del Modelo Intervalo Fijo : Almacena datos necesarios para calcular el Stock de Seguridad para cada artículo que utilice este modelo.

Calculo del CGI: Permite calcular el valor del CGI para cada artículo en base a la demanda estimada para el último periodo, utilizando la fórmula:

CGI=P×D+Ca× (Q/2) + Cp× (Q/D)
​

donde:

P: Precio por unidad del artículo

D: Demanda anual

Ca: Costo de almacenamiento anual

Q: Lote óptimo a pedir o comprar

Cp: Costo de pedido del proveedor por cada pedido

Listado de productos a Reponer: Genera un listado de los artículos que hayan alcanzado el punto de pedido (o estén por debajo) y no tengan una orden de compra pendiente.
Listado de productos Faltantes

Genera un listado de los productos que hayan alcanzado el stock de seguridad (o estén por debajo).

3. Modulo Orden de Compra
   
Alta de Órdenes de Compra: El sistema sugiere el proveedor predeterminado y el tamaño del lote, pero permite modificaciones.

Verificación de existencia de otra orden activa: Informa al usuario si existe otra orden de compra activa para el mismo artículo.

Al finalizar la orden el sistema debe actualizar el inventario del producto que se ordenó

4. Modulo Demanda

Permite Alta, Baja y Modificación (A/B/M) de demandas históricas por artículo y periodo.
Carga de Parámetros Generales del módulo

Define la cantidad de periodos a predecir por corrida.
Selecciona el método de cálculo del error a utilizar.
Establece el error aceptable.

Predicción de la demanda por diferentes métodos

Promedio Móvil Ponderado: Permite modificar el factor de ponderación y la cantidad de periodos históricos a utilizar.

Suavización Exponencial: Permite modificar el valor del coeficiente
α y el valor de la predicción raíz.

Genera automáticamente la predicción para el periodo siguiente utilizando el método seleccionado y crea una orden de compra en estado pendiente, verificando el stock del producto e informando al usuario.
