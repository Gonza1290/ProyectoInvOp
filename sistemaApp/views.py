from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Articulo, OrdenCompra, EstadoOrdenCompra,DemandaHistorica,ErrorType
from .forms import OrdenCompraForm,PromedioMovilForm,PromedioMovilPonderadoForm,SuavizacionExponencialForm,ModeloLoteFijoForm,ModeloIntervaloFijoForm
from django import forms
from datetime import datetime

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
                orden_compra.save()
                messages.success(request, f'Se ha creado una orden de compra para {articulo.nombreArticulo}.')
                return redirect('/admin/sistemaApp/accione/')
            else:
                messages.error(request, f'Ya existen ordenes pendientes o enviadas para {articulo.nombreArticulo}.')
    else:
        form = OrdenCompraForm(initial={'articulo': articulo_inicial, 'proveedor': proveedor_defecto})
    
    return render(request, 'crear_orden_compra.html', {'form': form})

def marcar_orden_recibida(request,orden_compra_id):
    orden_compra=OrdenCompra.objects.get(pk=orden_compra_id)
    estado_recibida = get_object_or_404(EstadoOrdenCompra, nombreEOC='Recibido')
    orden_compra.estadoOrdenCompra =estado_recibida
    orden_compra.save()
    articulo = Articulo.objects.get(pk=orden_compra.articulo.id)
    articulo.stockActual += orden_compra.cantidadLote
    articulo.save()
    return redirect('/admin/sistemaApp/ordencompra/')


#Modulo Demanda
def predecir_demanda_view(request,articulo_id):
    # Obtener el formulario seleccionado de la sesión o usar uno predefinido
    formulario_seleccionado = request.session.get('formulario_seleccionado', 'PromedioMovil')
    form = PromedioMovilForm()

    if 'Boton1' in request.POST:
        formulario_seleccionado = 'PromedioMovil'
        form = PromedioMovilForm(request.POST)
         # Guardar en la sesión
        request.session['formulario_seleccionado'] = formulario_seleccionado

    elif 'Boton2' in request.POST:
        formulario_seleccionado = 'PromedioMovilPonderado'
        form = PromedioMovilPonderadoForm(request.POST)
         # Guardar en la sesión
        request.session['formulario_seleccionado'] = formulario_seleccionado

    elif 'Boton3' in request.POST:
        formulario_seleccionado = 'SuavizacionExponencial'
        form = SuavizacionExponencialForm(request.POST)
         # Guardar en la sesión
        request.session['formulario_seleccionado'] = formulario_seleccionado


     # Si es un POST
    if request.method == 'POST':
        if formulario_seleccionado == 'PromedioMovil':
            form = PromedioMovilForm(request.POST)
            if form.is_valid():
                periodos = form.cleaned_data['periodosConsiderados']
                mes_actual = datetime.now().month
                rango_meses = range(mes_actual - periodos + 1, mes_actual + 1)
                demanda_historicas = DemandaHistorica.objects.filter(mes__in=rango_meses, articulo=articulo_id)

                if demanda_historicas.count() != periodos:
                    messages.error(request, "Cantidad de Demandas Historicas insuficientes")
                else:
                    demanda_predecida = sum(demanda_historica.cantidadDemanda for demanda_historica in demanda_historicas) / periodos
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


def cgi_view(request,articulo_id):
    #Obtengo el articulo
    articulo = Articulo.objects.get(pk=articulo_id)
    # Obtener el modelo predefinido para el articulo
    modelo_inventario_seleccionado = articulo.familiaArticulo.modeloInventario.nombreMI
    
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    #Obtengo el articulo
    articulo = Articulo.objects.get(pk=articulo_id)
    modelo_inventario = articulo.familiaArticulo.modeloInventario.nombreMI
    if modelo_inventario == 'Modelo Lote Fijo':
        demanda_predecida = articulo.demandaPredecida
        costo_almacentamiento= articulo.costoAlmacenamiento
        costo_pedido= articulo.proveedor_predefinido.costoPorPedido
        demora_proveedor= articulo.proveedor_predefinido.demoraPedido
        lote_optimo= (2*demanda_predecida*(costo_pedido/costo_almacentamiento))**0,5
        dias_habiles_mesual=30
        demanda_diaria= demanda_predecida/dias_habiles_mesual
        punto_pedido= demanda_diaria*demora_proveedor
        
        return redirect('/admin/sistemaApp/accione/')
    elif modelo_inventario == 'Modelo Intervalo Fijo':
        return redirect('/admin/sistemaApp/accione/')
    else:
        return redirect('/admin/sistemaApp/accione/')