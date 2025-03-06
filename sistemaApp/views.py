from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Articulo, OrdenCompra, EstadoOrdenCompra,DemandaHistorica,ErrorType
from .forms import OrdenCompraForm,PromedioMovilForm,PromedioMovilPonderadoForm,SuavizacionExponencialForm,ModeloLoteFijoForm,ModeloIntervaloFijoForm,OrdenVentaForm
from django import forms
from datetime import datetime
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from .utils import generar_rango_meses, obtener_nombre_mes

def index(request):
    return redirect('/admin/')

#Modulo Orden Compra
def crear_orden_compra(request, articulo_id):
    articulo_inicial = get_object_or_404(Articulo, pk=articulo_id)
    estado_enviada = get_object_or_404(EstadoOrdenCompra, nombreEOC='Enviada')
    proveedor_defecto = articulo_inicial.proveedor_predefinido
    
    if request.method == 'POST':
        form = OrdenCompraForm(request.POST)
        if form.is_valid():
            articulo = form.cleaned_data['articulo']
            estado_pendiente = get_object_or_404(EstadoOrdenCompra, nombreEOC='Pendiente')
            ordenes_pend_enviada = OrdenCompra.objects.filter(
                articulo=articulo,
                estadoOrdenCompra__in=[estado_enviada, estado_pendiente]
            )
            if not ordenes_pend_enviada.exists():
                orden_compra = form.save(commit=False)
                orden_compra.estadoOrdenCompra = estado_enviada
                orden_compra.montoTotal = articulo.precioVenta * form.cleaned_data['cantidadLote']
                orden_compra.save()
                messages.success(request, f'Se ha creado una orden de compra para {articulo.nombreArticulo}.')
                return redirect('/admin/sistemaApp/accione/')
            else:
                messages.error(request, f'Ya existen ordenes pendientes o enviadas para {articulo.nombreArticulo}.')
    else:
        form = OrdenCompraForm(initial={'articulo': articulo_inicial, 'proveedor': proveedor_defecto})
    
    return render(request, 'crear_orden_compra.html', {'form': form})

def marcar_orden_recibida(request, orden_compra_id):
    try:
        orden_compra = OrdenCompra.objects.get(pk=orden_compra_id)
        estado_recibida = EstadoOrdenCompra.objects.get(nombreEOC='Recibido')
    except OrdenCompra.DoesNotExist:
        messages.error(request, "Orden de compra no encontrada")
        return redirect('/admin/sistemaApp/ordencompra/')
    except EstadoOrdenCompra.DoesNotExist:
        messages.error(request, "Estado 'Recibido' no encontrado")
        return redirect('/admin/sistemaApp/ordencompra/')

    orden_compra.estadoOrdenCompra = estado_recibida
    orden_compra.save()

    articulo = Articulo.objects.get(pk=orden_compra.articulo.id)
    articulo.stockActual += orden_compra.cantidadLote
    articulo.save()

    return redirect('/admin/sistemaApp/ordencompra/')

def enviar_orden_compra(request,orden_compra_id):
    orden_compra=OrdenCompra.objects.get(pk=orden_compra_id)
    estado = get_object_or_404(EstadoOrdenCompra, nombreEOC='Enviada')
    orden_compra.estadoOrdenCompra =estado
    orden_compra.save()
    return redirect('/admin/sistemaApp/ordencompra/')

def cancelar_orden_compra(request,orden_compra_id):
    orden_compra=OrdenCompra.objects.get(pk=orden_compra_id)
    estado = get_object_or_404(EstadoOrdenCompra, nombreEOC='Cancelada')
    orden_compra.estadoOrdenCompra =estado
    orden_compra.save()
    return redirect('/admin/sistemaApp/ordencompra/')

#Modulo Demanda
def predecir_demanda_view(request, articulo_id):
    # Obtener el formulario seleccionado de la sesión o usar uno predefinido
    formulario_seleccionado = request.session.get('formulario_seleccionado', 'PromedioMovil')
    form = get_formulario(formulario_seleccionado)

    # Definir el formulario a mostrar
    if 'Boton1' in request.POST:
        formulario_seleccionado = 'PromedioMovil'
        form = get_formulario(formulario_seleccionado)
        request.session['formulario_seleccionado'] = formulario_seleccionado
        context = {
            'formulario_seleccionado': formulario_seleccionado,
            'form': form,
        }
        return render(request, 'demanda_opciones.html', context)

    elif 'Boton2' in request.POST:
        formulario_seleccionado = 'PromedioMovilPonderado'
        form = get_formulario(formulario_seleccionado)
        request.session['formulario_seleccionado'] = formulario_seleccionado
        context = {
            'formulario_seleccionado': formulario_seleccionado,
            'form': form,
        }
        return render(request, 'demanda_opciones.html', context)

    elif 'Boton3' in request.POST:
        formulario_seleccionado = 'SuavizacionExponencial'
        form = get_formulario(formulario_seleccionado)
        request.session['formulario_seleccionado'] = formulario_seleccionado
        context = {
            'formulario_seleccionado': formulario_seleccionado,
            'form': form,
        }
        return render(request, 'demanda_opciones.html', context)

    # Si es un POST en el formulario seleccionado
    if request.method == 'POST':
        form = get_formulario(formulario_seleccionado, request.POST)
        if form.is_valid():
            resultados = procesar_formulario(request, form, formulario_seleccionado, articulo_id)
            if resultados:
                return render(request, 'resultados_prediccion.html', resultados)
        else:
            messages.error(request, 'Formulario inválido')

    # Sacar los field is required del form
    if form.errors:
        for field in form.errors:
            form.errors[field] = [error for error in form.errors[field] if error != 'This field is required.']

    # Si es un GET o si ninguno de los formularios fue válido
    context = {
        'formulario_seleccionado': formulario_seleccionado,
        'form': form,
    }
    return render(request, 'demanda_opciones.html', context)

def get_formulario(formulario_seleccionado, data=None):
    if formulario_seleccionado == 'PromedioMovil':
        return PromedioMovilForm(data)
    elif formulario_seleccionado == 'PromedioMovilPonderado':
        return PromedioMovilPonderadoForm(data)
    elif formulario_seleccionado == 'SuavizacionExponencial':
        return SuavizacionExponencialForm(data)
    return PromedioMovilForm(data)

def procesar_formulario(request, form, formulario_seleccionado, articulo_id):
    if formulario_seleccionado == 'PromedioMovil':
        return procesar_promedio_movil(request, form, articulo_id)
    elif formulario_seleccionado == 'PromedioMovilPonderado':
        return procesar_promedio_movil_ponderado(request, form, articulo_id)
    elif formulario_seleccionado == 'SuavizacionExponencial':
        return procesar_suavizacion_exponencial(request, form, articulo_id)
    return None

def procesar_promedio_movil(request, form, articulo_id):
    periodos = form.cleaned_data['periodosConsiderados']
    mes_a_predecir = form.cleaned_data['mes_a_predecir']
    rango_meses = generar_rango_meses(mes_a_predecir, periodos)

    demanda_historicas = DemandaHistorica.objects.filter(
        Q(articulo=articulo_id) & 
        Q(mes__in=[mes for mes, anio in rango_meses]) & 
        Q(año__in=[anio for mes, anio in rango_meses])
    )

    if demanda_historicas.count() != periodos:
        messages.error(request, "Cantidad de Demandas Historicas insuficientes")
        return None

    demanda_predecida = sum(demanda_historica.cantidadDemanda for demanda_historica in demanda_historicas) / periodos
    metodo_error = form.cleaned_data['metodoError']
    try:
        anio_actual = datetime.now().year
        demanda_real_proxima = DemandaHistorica.objects.get(mes=mes_a_predecir, articulo=articulo_id,año = anio_actual).cantidadDemanda
    except DemandaHistorica.DoesNotExist:
        demanda_real_proxima = None

    if demanda_real_proxima is not None:  
        error_aceptable = form.cleaned_data['errorAceptable']
        error_calculado, decision, diferencia_real_pronostico = calcularError(demanda_real_proxima, demanda_predecida, error_aceptable, metodo_error, articulo_id)
    else:
        demanda_real_proxima = 'No disponible para calcular error'
        error_calculado = 'No disponible'
        error_aceptable = 'No disponible'
        decision = 'No disponible'
        diferencia_real_pronostico = 'No disponible'

    nombre_mes = obtener_nombre_mes(mes_a_predecir)
    return {
        'mes_a_predecir': nombre_mes,
        'demanda_predecida': demanda_predecida,
        'demanda_real_proxima': demanda_real_proxima,
        'error_calculado': error_calculado,
        'error_aceptable': error_aceptable,
        'diferencia_real_pronostico': diferencia_real_pronostico,
        'decision': decision,
    }

def procesar_promedio_movil_ponderado(request, form, articulo_id):
    periodos = form.cleaned_data['periodosConsiderados']
    ponderaciones = form.cleaned_data['ponderaciones']
    mes_a_predecir = form.cleaned_data['mes_a_predecir']
    rango_meses = generar_rango_meses(mes_a_predecir, periodos)

    demanda_historicas = DemandaHistorica.objects.filter(
        Q(articulo=articulo_id) & 
        Q(mes__in=[mes for mes, anio in rango_meses]) & 
        Q(año__in=[anio for mes, anio in rango_meses])
    )

    if demanda_historicas.count() != periodos:
        messages.error(request, "Cantidad de Demandas Historicas insuficientes")
        return None
    if periodos != len(ponderaciones):
        messages.error(request, "Cantidad de Ponderaciones y Periodos distintos")
        return None

    demanda_predecida = sum(demanda_historica.cantidadDemanda * ponderacion for demanda_historica, ponderacion in zip(demanda_historicas, ponderaciones)) / sum(ponderaciones)
    metodo_error = form.cleaned_data['metodoError']
    try:
        anio_actual = datetime.now().year
        demanda_real_proxima = DemandaHistorica.objects.get(mes=mes_a_predecir, articulo=articulo_id,año = anio_actual).cantidadDemanda
    except DemandaHistorica.DoesNotExist:
        demanda_real_proxima = None

    if demanda_real_proxima is not None:  
        error_aceptable = form.cleaned_data['errorAceptable']
        error_calculado, decision, diferencia_real_pronostico = calcularError(demanda_real_proxima, demanda_predecida, error_aceptable, metodo_error, articulo_id)
    else:
        demanda_real_proxima = 'No disponible para calcular error'
        error_calculado = 'No disponible'
        error_aceptable = 'No disponible'
        decision = 'No disponible'
        diferencia_real_pronostico = 'No disponible'

    nombre_mes = obtener_nombre_mes(mes_a_predecir)
    return {
        'mes_a_predecir': nombre_mes,
        'demanda_predecida': demanda_predecida,
        'demanda_real_proxima': demanda_real_proxima,
        'error_calculado': error_calculado,
        'error_aceptable': error_aceptable,
        'diferencia_real_pronostico': diferencia_real_pronostico,
        'decision': decision,
    }

def procesar_suavizacion_exponencial(request, form, articulo_id):
    mes_a_predecir = datetime.now().month
    anio_actual = datetime.now().year
    try:
        demanda_real_anterior = DemandaHistorica.objects.get(mes=mes_a_predecir-1, articulo=articulo_id,año = anio_actual).cantidadDemanda
    except DemandaHistorica.DoesNotExist:
        demanda_real_anterior = None
        
    if demanda_real_anterior is not None: 
        # Calcular demanda predecida 
        prediccion_mes_anterior = form.cleaned_data['prediccionDemanda']
        coef_suavizacion = form.cleaned_data['coefSuavizacion']
        demanda_predecida = prediccion_mes_anterior + coef_suavizacion * (demanda_real_anterior - prediccion_mes_anterior)
        
        
        nombre_mes = obtener_nombre_mes(mes_a_predecir)
        return {
            'mes_a_predecir': nombre_mes,
            'demanda_real_anterior': demanda_real_anterior,
            'prediccion_mes_anterior': prediccion_mes_anterior,
            'demanda_predecida': demanda_predecida,
        }
    else:
        messages.error(request, "No se puede calcular la demanda ya que no se tiene la demanda real del mes anterior")
        

#Funcion para calcular error de prediccion demanda
def calcularError(demanda_real_proxima,demanda_predecida,error_aceptable,metodo_error,articulo_id):
    if metodo_error == ErrorType.MAD:
        error_calculado = abs(demanda_real_proxima - demanda_predecida)
    elif metodo_error == ErrorType.MSE:
        error_calculado = (demanda_real_proxima - demanda_predecida) ** 2
    else:
        error_calculado = (abs(demanda_real_proxima - demanda_predecida)/ demanda_real_proxima)*100

    diferencia_real_pronostico = (abs(demanda_real_proxima - demanda_predecida)/ demanda_real_proxima)*100
    if error_aceptable >= diferencia_real_pronostico:
        decision = 'Aceptado'
        #Guardar demanda predecida
        articulo= Articulo.objects.get(pk= articulo_id)
        articulo.demandaPredecida = demanda_predecida
        articulo.save()
    else:
        decision = 'Rechazado'

    return error_calculado, decision,diferencia_real_pronostico

#Modulo Inventario
def cgi_view(request,articulo_id):
    #Obtengo el articulo
    articulo = Articulo.objects.get(pk=articulo_id)
    # Obtener el modelo predefinido para el articulo
    modelo_inventario_seleccionado = articulo.categoria.modeloInventario.nombreMI
    
    if modelo_inventario_seleccionado == 'Modelo Lote Fijo':
        form = ModeloLoteFijoForm()
    else :
        form = ModeloIntervaloFijoForm()

    # Si es un POST
    if request.method == 'POST':
        if modelo_inventario_seleccionado == 'Modelo Lote Fijo':
            form = ModeloLoteFijoForm(request.POST)
            if form.is_valid():
                demanda_anual = form.cleaned_data['demandaAnual']
                dias_laborales_anual = form.cleaned_data['diasLaboralesAnual']
                costo_almacentamiento= articulo.costoAlmacenamiento
                costo_pedido= articulo.proveedor_predefinido.costoPorPedido
                demora_proveedor= articulo.proveedor_predefinido.demoraPedido
                #Calculo
                lote_optimo= round((2*demanda_anual*(costo_pedido/costo_almacentamiento))**0.5)
                demanda_diaria= round(demanda_anual/dias_laborales_anual)
                punto_pedido= demanda_diaria*demora_proveedor
                numero_pedidos= round(demanda_anual / lote_optimo)
                tiempo_entre_pedidos= round(dias_laborales_anual/numero_pedidos)

                #Calculo CGI
                costo_compra = articulo.precioVenta * demanda_anual
                costo_almacentamiento_total = costo_almacentamiento * (lote_optimo/2)
                costo_pedido_total= costo_pedido * (demanda_anual/lote_optimo)
                cgi = costo_compra + costo_almacentamiento_total + costo_pedido_total
                
                resultados = {
                    'demanda_anual': demanda_anual,
                    'demanda_diaria': demanda_diaria,
                    'costo_almacentamiento': costo_almacentamiento,
                    'costo_pedido': costo_pedido,
                    'lote_optimo': lote_optimo,
                    'punto_pedido': punto_pedido,
                    'numero_pedidos': numero_pedidos,
                    'tiempo_entre_pedidos': tiempo_entre_pedidos,
                    'cgi': cgi,
                }
                
                #Guardar Resultados
                articulo.loteOptimo = lote_optimo
                articulo.puntoPedido = punto_pedido
                articulo.numeroPedidos= numero_pedidos
                articulo.tiempoEntrePedidos = tiempo_entre_pedidos
                articulo.save()
                return render(request, 'resultados_cgi.html', resultados)
            
        elif modelo_inventario_seleccionado == 'Modelo Intervalo Fijo':
            form = ModeloIntervaloFijoForm(request.POST)
            if form.is_valid():
                demanda_anual = form.cleaned_data['demandaAnual']
                dias_laborales_anual = form.cleaned_data['diasLaboralesAnual']
                tasa_produccion_anual = form.cleaned_data['tasaProduccionAnual']
                costo_almacentamiento= articulo.costoAlmacenamiento
                costo_pedido= form.cleaned_data['costoOrdenProduccion']
                demora_proveedor= articulo.proveedor_predefinido.demoraPedido
                #Calculo
                lote_optimo= round((2*demanda_anual*(costo_pedido/costo_almacentamiento)*(1/(1 - demanda_anual/tasa_produccion_anual)))**0.5)
                demanda_diaria= round(demanda_anual/dias_laborales_anual)
                punto_pedido= demanda_diaria*demora_proveedor
                numero_pedidos= round(demanda_anual / lote_optimo)
                tiempo_entre_pedidos= round(((2/demanda_anual)*(costo_pedido/costo_almacentamiento)*(1/(1 - demanda_anual/tasa_produccion_anual)))**0.5)
                
                #Calculo CGI
                costo_compra = articulo.precioVenta * demanda_anual
                costo_almacentamiento_total = costo_almacentamiento * (lote_optimo/2)
                costo_pedido_total= costo_pedido * (demanda_anual/lote_optimo)
                cgi = costo_compra + costo_almacentamiento_total + costo_pedido_total
                
                resultados = {
                    'demanda_anual': demanda_anual,
                    'demanda_diaria': demanda_diaria,
                    'costo_almacentamiento': costo_almacentamiento,
                    'costo_pedido': costo_pedido,
                    'lote_optimo': lote_optimo,
                    'punto_pedido': punto_pedido,
                    'numero_pedidos': numero_pedidos,
                    'tiempo_entre_pedidos': tiempo_entre_pedidos,
                    'cgi': cgi,
                }
                
                #Guardar Resultados
                articulo.loteOptimo = lote_optimo
                articulo.puntoPedido = punto_pedido
                articulo.numeroPedidos= numero_pedidos
                articulo.tiempoEntrePedidos = tiempo_entre_pedidos
                articulo.save()
                return render(request, 'resultados_cgi.html', resultados)

    #Sacar los field is required del form
    if form.errors:
        for field in form.errors:
            form.errors[field] = [error for error in form.errors[field] if error != 'This field is required.']
    # Si es un GET o si ninguno de los formularios fue válido
    context = {
        'modelo_inventario_seleccionado': modelo_inventario_seleccionado,
        'form': form,
    }
    return render(request, 'cgi_view.html', context)

#Modulo Ventas
def crear_orden_venta(request,articulo_id):
    articulo_inicial = get_object_or_404(Articulo, pk=articulo_id)

    if request.method == 'POST':
        form = OrdenVentaForm(request.POST)
        if form.is_valid():
            articulo = form.cleaned_data['articulo']
            cantidad_vendida = form.cleaned_data['cantidadVendida']
            #Si no tengo stock
            if articulo.stockActual < cantidad_vendida:
                messages.error(request,f'Stock insuficiente de {articulo.nombreArticulo}, stock actual: {articulo.stockActual}')
            else:
                precio_articulo = articulo.precioVenta
                monto_total = precio_articulo * cantidad_vendida
                fecha_hora_venta= datetime.now()
                orden_venta = form.save(commit=False)
                orden_venta.montoTotal = monto_total
                orden_venta.fechaHoraVenta = fecha_hora_venta
                orden_venta.save()
                articulo.stockActual -= cantidad_vendida
                articulo.save()
                messages.success(request,f'Se ha generado la orden de venta para {articulo.nombreArticulo}')
                #Generar Orden compra automatica si stock actual alcanzo el punto pedido
                if articulo.stockActual <= articulo.puntoPedido:
                    estado_pendiente = get_object_or_404(EstadoOrdenCompra, nombreEOC='Pendiente')
                    orden_compra = OrdenCompra.objects.create(
                        cantidadLote=articulo.loteOptimo, 
                        montoTotal= articulo.precioVenta * articulo.loteOptimo,
                        estadoOrdenCompra=estado_pendiente,
                        articulo= articulo,
                        proveedor=  articulo.proveedor_predefinido,
                    )
                    orden_compra.save()
                    messages.success(request,f'Se ha generado la orden de compra para {articulo.nombreArticulo}')
                return redirect('/admin/sistemaApp/accione/')
    else:
        
        form = OrdenVentaForm(initial={'articulo': articulo_inicial})
    return render(request, 'crear_orden_venta.html', {'form': form})

# Modulo Ayuda
@staff_member_required
def help(request):
    return render(request, 'help.html')
