from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import path
from .models import Articulo, OrdenCompra, EstadoOrdenCompra    
from .forms import OrdenCompraForm
# Create your views here.

def crear_orden_compra(request, articulo_id):
    articulo = get_object_or_404(Articulo, pk=articulo_id)
    estado_enviada = get_object_or_404(EstadoOrdenCompra, nombreEOC='enviada')
    
    if request.method == 'POST':
        form = OrdenCompraForm(request.POST, instance=articulo)
        if form.is_valid():
            orden_compra = form.save(commit=False)
            orden_compra.articulo = articulo
            orden_compra.estadoOrdenCompra = estado_enviada
            orden_compra.save()
            messages.success(request, f'Se ha creado una orden de compra para {articulo.nombreArticulo}.')
            return redirect('admin')
    else:
        form = OrdenCompraForm(articulo=articulo)

    return render(request, 'admin/crear_orden_compra.html', {'form': form, 'articulo': articulo})