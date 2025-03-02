from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Articulo, OrdenCompra, EstadoOrdenCompra,DemandaHistorica,ErrorType
from .forms import OrdenCompraForm,PromedioMovilForm,PromedioMovilPonderadoForm,SuavizacionExponencialForm,ModeloLoteFijoForm,ModeloIntervaloFijoForm,OrdenVentaForm
from django import forms
from datetime import datetime
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
import calendar

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
                orden_compra.montoTotal = articulo.precioArticulo * form.cleaned_data['cantidadLote']
                orden_compra.save()
                messages.success(request, f'Se ha creado una orden de compra para {articulo.nombreArticulo}.')
                return redirect('/admin/sistemaApp/accione/')
            else:
                messages.error(request, f'Ya existen ordenes pendientes o enviadas para {articulo.nombreArticulo}.')
    else:
        form = OrdenCompraForm(initial={'articulo': articulo_inicial, 'proveedor': proveedor_defecto})
    
    return render(request, 'crear_orden_compra.html', {'form': form})

from django.contrib import messages

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
def predecir_demanda_view(request,articulo_id):
    # Obtener el formulario seleccionado de la sesión o usar uno predefinido
    formulario_seleccionado = request.session.get('formulario_seleccionado', 'PromedioMovil')
    form = PromedioMovilForm()

    # Definir el formulario a mostrar
    if 'Boton1' in request.POST:
        formulario_seleccionado = 'PromedioMovil'
        form = PromedioMovilForm()
         # Guardar en la sesión
        request.session['formulario_seleccionado'] = formulario_seleccionado

    elif 'Boton2' in request.POST:
        formulario_seleccionado = 'PromedioMovilPonderado'
        form = PromedioMovilPonderadoForm()
         # Guardar en la sesión
        request.session['formulario_seleccionado'] = formulario_seleccionado

    elif 'Boton3' in request.POST:
        formulario_seleccionado = 'SuavizacionExponencial'
        form = SuavizacionExponencialForm()
         # Guardar en la sesión
        request.session['formulario_seleccionado'] = formulario_seleccionado

    # Si es un POST en el formulario seleccionado
    if request.method == 'POST':
        if formulario_seleccionado == 'PromedioMovil':
            form = PromedioMovilForm(request.POST)
            if form.is_valid():
                periodos = form.cleaned_data['periodosConsiderados']
                mesApredicir = int(form.cleaned_data['mesApredecir'])
                anio_actual = datetime.now().year
                
                # Calcular el rango de meses considerando los años
                rango_meses = []
                for i in range(periodos):
                    mes = mesApredicir - i - 1
                    anio = anio_actual
                    if mes <= 0:
                        mes += 12
                        anio -= 1
                    rango_meses.append((mes, anio))

                print(rango_meses)

                # Filtrar las demandas históricas considerando los meses y años
                demanda_historicas = DemandaHistorica.objects.filter(
                    Q(articulo=articulo_id) & 
                    Q(mes__in=[mes for mes, anio in rango_meses]) & 
                    Q(año__in=[anio for mes, anio in rango_meses])
                )

                if demanda_historicas.count() != periodos:
                    messages.error(request, "Cantidad de Demandas Historicas insuficientes")
                else:
                    demanda_predecida = sum(demanda_historica.cantidadDemanda for demanda_historica in demanda_historicas) / periodos
                    metodo_error = form.cleaned_data['metodoError']
                    try:
                        demanda_real_proxima = DemandaHistorica.objects.get(mes=mesApredicir, articulo=articulo_id).cantidadDemanda
                    except DemandaHistorica.DoesNotExist:
                        demanda_real_proxima = None
                    #Si existe una demanda real proxima se calcula el error
                    if demanda_real_proxima is not None:  
                        error_aceptable = form.cleaned_data['errorAceptable']
                        error_calculado, decision, diferencia_real_pronostico = calcularError(demanda_real_proxima, demanda_predecida, error_aceptable, metodo_error,articulo_id)
                    else:
                        demanda_real_proxima = 'No disponible para calcular error'
                        error_calculado = 'No disponible'
                        error_aceptable = 'No disponible'
                        decision = 'No disponible'
                        diferencia_real_pronostico = 'No disponible'
                    
                    nombre_mes = obtener_nombre_mes(mesApredicir)
                    
                    resultados = {
                        'mes_a_predecir': nombre_mes,
                        'demanda_predecida': demanda_predecida,
                        'error_calculado': error_calculado,
                        'error_aceptable': error_aceptable,
                        'diferencia_real_pronostico': diferencia_real_pronostico,
                        'decision': decision,
                    }
                    return render(request, 'resultados_prediccion.html', resultados)

        elif formulario_seleccionado == 'PromedioMovilPonderado':
            form = PromedioMovilPonderadoForm(request.POST)
            if form.is_valid():
                periodos = form.cleaned_data['periodosConsiderados']
                ponderaciones = form.cleaned_data['ponderaciones']
                mes_actual = datetime.now().month
                rango_meses = range(mes_actual - periodos + 1, mes_actual + 1)
                demanda_historicas = DemandaHistorica.objects.filter(mes__in=rango_meses, articulo=articulo_id)

                if demanda_historicas.count() != periodos:
                    messages.error(request, "Cantidad de Demandas Historicas insuficientes")
                elif periodos != len(ponderaciones):
                    messages.error(request, "Cantidad de Ponderaciones y Periodos distintos")
                else:
                    demanda_predecida = sum(demanda_historica.cantidadDemanda * ponderacion for demanda_historica, ponderacion in zip(demanda_historicas, ponderaciones)) / sum(ponderaciones)
                    metodo_error = form.cleaned_data['metodoError']
                    demanda_real_proxima = DemandaHistorica.objects.get(mes=mes_actual + 1, articulo=articulo_id).cantidadDemanda
                    error_aceptable = form.cleaned_data['errorAceptable']

                    demanda_real_proxima = DemandaHistorica.objects.get(mes=mes_actual + 1, articulo=articulo_id).cantidadDemanda

                    error_calculado, decision,diferencia_real_pronostico = calcularError(demanda_real_proxima, demanda_predecida, error_aceptable, metodo_error,articulo_id)
                    resultados = {
                        'demanda_predecida': demanda_predecida,
                        'error_calculado': error_calculado,
                        'error_aceptable': error_aceptable,
                        'diferencia_real_pronostico': diferencia_real_pronostico,
                        'decision': decision,
                    }
                    return render(request, 'resultados_prediccion.html', resultados)
        elif formulario_seleccionado == 'SuavizacionExponencial':
            form = SuavizacionExponencialForm(request.POST)
            if form.is_valid():
                mes_actual = datetime.now().month
                demanda_real = DemandaHistorica.objects.get(mes=mes_actual-1).cantidadDemanda
                ultima_prediccion_demanda = form.cleaned_data['prediccionDemanda']
                coef_suavizacion = form.cleaned_data['coefSuavizacion']
                demanda_predecida= ultima_prediccion_demanda + coef_suavizacion*(demanda_real-ultima_prediccion_demanda)

                metodo_error = form.cleaned_data['metodoError']
                demanda_real_proxima = DemandaHistorica.objects.get(mes=mes_actual + 1, articulo=articulo_id).cantidadDemanda
                error_aceptable = form.cleaned_data['errorAceptable']
                error_calculado, decision,diferencia_real_pronostico = calcularError(demanda_real_proxima, demanda_predecida, error_aceptable, metodo_error,articulo_id)
                resultados = {
                    'demanda_predecida': demanda_predecida,
                    'error_calculado': error_calculado,
                    'error_aceptable': error_aceptable,
                    'diferencia_real_pronostico': diferencia_real_pronostico,
                    'decision': decision,
                }
                return render(request, 'resultados_prediccion.html', resultados)
        else:
            messages.error('formulario invalido')
            
    #Sacar los field is required del form
    if form.errors:
        for field in form.errors:
            form.errors[field] = [error for error in form.errors[field] if error != 'This field is required.']
    # Si es un GET o si ninguno de los formularios fue válido
    context = {
        'formulario_seleccionado': formulario_seleccionado,
        'form': form,
    }
    return render(request, 'demanda_opciones.html', context)

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
                costo_compra = articulo.precioArticulo * demanda_anual
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
                costo_compra = articulo.precioArticulo * demanda_anual
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
                precio_articulo = articulo.precioArticulo
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
                        montoTotal= articulo.precioArticulo * articulo.loteOptimo,
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

#Funciones Auxiliares
def obtener_nombre_mes(numero_mes):
    return calendar.month_name[numero_mes]