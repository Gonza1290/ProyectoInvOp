from django import forms
from .models import OrdenCompra,ErrorType
from django.core.validators import MinValueValidator, MaxValueValidator
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
    errorAceptable = forms.IntegerField(
        label='Error Aceptable (%)',
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Ingrese un valor entre 1 y 100'
    )

class PromedioMovilPonderadoForm(forms.Form):
    periodosConsiderados = forms.IntegerField(label='Periodos Históricos Considerados')
    metodoError = forms.ChoiceField(
        label='Método de error a usar',
        choices=ErrorType.choices,
        initial=ErrorType.MAD
    )
    ponderaciones = forms.CharField(
        label='Ponderacion de Periodos Históricos Considerados',
        help_text='Ingrese los periodos separados por comas (ej. 1,2,3,4,5)',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    errorAceptable = forms.IntegerField(
        label='Error Aceptable (%)',
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Ingrese un valor entre 1 y 100'
    )
    def clean_ponderaciones(self):
        ponderaciones = self.cleaned_data.get('ponderaciones')
        
        if isinstance(ponderaciones, int):
            ponderaciones = str(ponderaciones)  # Convertir a cadena si es un entero
        
        try:
            ponderaciones = [int(periodo.strip()) for periodo in ponderaciones.split(',')]
        except AttributeError:
            raise forms.ValidationError('Ingrese valores numéricos separados por comas.')
        except ValueError:
            raise forms.ValidationError('Ingrese valores numéricos separados por comas válidos.')

        return ponderaciones

class SuavizacionExponencialForm(forms.Form):
    prediccionDemanda = forms.IntegerField(label='Predicción Demanda Último Periodo')
    coefSuavizacion = forms.DecimalField(label='Coeficiente de Suavización',min_value=0.0,max_value=1.0,initial=0.05)
    metodoError = forms.ChoiceField(
        label='Método de error a usar',
        choices=ErrorType.choices,
        initial=ErrorType.MAD
    )
    errorAceptable = forms.IntegerField(
        label='Error Aceptable (%)',
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Ingrese un valor entre 1 y 100'
    )