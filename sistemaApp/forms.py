from django import forms
from .models import OrdenCompra,Articulo

class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['cantidadLote', 'proveedor']

    def __init__(self, *args, **kwargs):
        super(OrdenCompraForm,self).__init__(*args, **kwargs)
        
        #Proveedor por defecto
        self.fields['proveedor'].initial = instance.proveedor_predefinido.nombreProveedor