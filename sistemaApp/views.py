from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Articulo, OrdenCompra, EstadoOrdenCompra,DemandaHistorica
from .forms import OrdenCompraForm,PromedioMovilForm,PromedioMovilPonderadoForm,SuavizacionExponencialForm
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
    formulario_seleccionado = 'PromedioMovil'  # Metodo por defecto
    form = PromedioMovilForm()

    #Si se acciona Boton 1
    if 'Boton1' in request.POST:
        formulario_seleccionado = 'PromedioMovil'
        form = PromedioMovilForm()
        context = {'formulario_seleccionado': formulario_seleccionado,'form': form,}
        return render(request, 'demanda_opciones.html', context)
    #Si se acciona Boton 2
    if 'Boton2' in request.POST:
        formulario_seleccionado = 'PromedioMovilPonderado'
        form = PromedioMovilPonderadoForm()
        context = {'formulario_seleccionado': formulario_seleccionado,'form': form,}
        return render(request, 'demanda_opciones.html', context)
    #Si se acciona Boton 3
    if 'Boton3' in request.POST:
        formulario_seleccionado = 'SuavizacionExponencial'
        form = SuavizacionExponencialForm()
        context = {'formulario_seleccionado': formulario_seleccionado,'form': form,}
        return render(request, 'demanda_opciones.html', context)
        
    #SI ES UN POST
    if request.method == 'POST':
        if formulario_seleccionado == 'PromedioMovil':
            form = PromedioMovilForm(request.POST)
            if form.is_valid():
                periodos = form.cleaned_data['periodosConsiderados']
                mes_actual = datetime.now().month
                rango_meses= range(mes_actual-periodos+1,mes_actual+1)
                demanda_historicas = DemandaHistorica.objects.filter(mes__in =rango_meses,articulo=articulo_id)
                
                if demanda_historicas.count() != periodos:
                    messages.error(request, "Cantidad de Demandas Historicas insuficientes")
                else:
                    demanda_predecida=0
                    for demanda_historica in demanda_historicas:
                        demanda_predecida += demanda_historica.cantidadDemanda
                    
                    demanda_predecida = demanda_predecida/ demanda_historicas.count()
                    resultados = {
                        'demanda_predecida': demanda_predecida,
                    }
                    return render(request, 'resultados_prediccion.html', resultados)
            
        elif formulario_seleccionado == 'PromedioMovilPonderado':
            form = PromedioMovilPonderadoForm(request.POST)
            if form.is_valid():
                periodos = form.cleaned_data['periodosConsiderados']
                # Generar dinámicamente campos adicionales
                for i in range(1, periodos + 1):
                    form.fields[f'ponderacion_{i}'] = forms.FloatField(label=f'Ponderación {i}')
                context = {
                    'formulario_seleccionado': formulario_seleccionado,
                    'form': form,
                }
                
                #submit_form nos indica el envio final del form
                if 'submit_form' in request.POST:
                    # Validar nuevamente el formulario completo
                    form = PromedioMovilPonderadoForm(request.POST)
                    if form.is_valid():
                        # Procesar los datos del formulario
                        return messages.success('Datos procesados correctamente')  
                    
        elif formulario_seleccionado == 'SuavizacionExponencial':
            form = SuavizacionExponencialForm(request.POST)

    #SI ES UN GET
    context = {
        'formulario_seleccionado': formulario_seleccionado,
        'form': form,
    }
    return render(request, 'demanda_opciones.html', context)