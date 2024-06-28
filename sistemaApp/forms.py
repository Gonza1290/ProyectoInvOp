from django import forms
from .models import OrdenCompra

class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['cantidadLote', 'proveedor', 'articulo']  

    def __init__(self, *args, **kwargs):
        super(OrdenCompraForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            initial = kwargs['initial']
            self.fields['articulo'].initial = initial.get('articulo')
            self.fields['proveedor'].initial = initial.get('proveedor')