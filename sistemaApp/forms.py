from django import forms
from .models import OrdenCompra,ErrorType

#Formulario OrdenCompra
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
            

from django import forms
from .models import ErrorType  # Asegúrate de importar ErrorType correctamente

# Formularios tipos de predicción demanda
class PromedioMovilForm(forms.Form):
    periodosConsiderados = forms.IntegerField(label='Periodos Históricos Considerados')
    metodoError = forms.ChoiceField(
        label='Método de error a usar',
        choices=ErrorType.choices,
        initial=ErrorType.MAD  # initial en lugar de default
    )
    errorAceptable = forms.DecimalField(
        label='Error Aceptable (%)',
        max_digits=2, decimal_places=2,  # Ajusta según tus necesidades de precisión
        initial=5.0  # Valor inicial del porcentaje aceptable
    )

class PromedioMovilPonderadoForm(forms.Form):
    periodosConsiderados = forms.IntegerField(label='Periodos Históricos Considerados')
    metodoError = forms.ChoiceField(
        label='Método de error a usar',
        choices=ErrorType.choices,
        initial=ErrorType.MAD
    )

class SuavizacionExponencialForm(forms.Form):
    prediccionDemanda = forms.IntegerField(label='Predicción Demanda Último Periodo')
    coefSuavizacion = forms.IntegerField(label='Coeficiente de Suavización')
