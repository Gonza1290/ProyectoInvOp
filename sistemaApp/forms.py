from django import forms
from .models import OrdenCompra,ErrorType,OrdenVenta,MedioPago
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from .utils import obtener_nombre_mes

# Enumeracion
MESES_CHOICES = [
        (1, 'Enero'),
        (2, 'Febrero'),
        (3, 'Marzo'),
        (4, 'Abril'),
        (5, 'Mayo'),
        (6, 'Junio'),
        (7, 'Julio'),
        (8, 'Agosto'),
        (9, 'Septiembre'),
        (10, 'Octubre'),
        (11, 'Noviembre'),
        (12, 'Diciembre'),
]

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
            
#Formulario OrdenVenta
class OrdenVentaForm(forms.ModelForm):
    class Meta:
        model = OrdenVenta
        fields = ['cantidadVendida', 'articulo','medioPago']  

    def __init__(self, *args, **kwargs):
        super(OrdenVentaForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            initial = kwargs['initial']
            self.fields['articulo'].initial = initial.get('articulo')
        self.fields['medioPago'].queryset = MedioPago.objects.all()

# Formularios tipos de predicción demanda
class PromedioMovilForm(forms.Form):
    periodosConsiderados = forms.IntegerField(label='Periodos Históricos Considerados (Meses)',initial=3)
    mes_a_predecir = forms.ChoiceField(
        label='Mes a predecir',
        choices=MESES_CHOICES,
        help_text='Solo el proximo mes o meses anteriores'
    )
    metodoError = forms.ChoiceField(
        label='Método de error a usar',
        choices=ErrorType.choices,
        initial=ErrorType.MAD, # initial en lugar de default
        help_text='Solo disponible si se tiene demanda real'
    )
    errorAceptable = forms.IntegerField(
        label='Error Aceptable (%)',
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Ingrese un valor entre 1 y 100',
        initial=5
    )
    
    def __init__(self, *args, **kwargs):
        super(PromedioMovilForm, self).__init__(*args, **kwargs)
        mes_actual = datetime.now().month
        self.fields['mes_a_predecir'].choices = [
            (mes, nombre) for mes, nombre in MESES_CHOICES if mes <= mes_actual + 1
        ]
        
    def clean_periodosConsiderados(self):
        periodos = self.cleaned_data.get('periodosConsiderados')
        if periodos <= 0:
            raise forms.ValidationError("El número de periodos debe ser mayor que cero.")
        return periodos
    
class PromedioMovilPonderadoForm(forms.Form):
    periodosConsiderados = forms.IntegerField(label='Periodos Históricos Considerados (Meses)',initial=3)
    mes_a_predecir = forms.ChoiceField(
        label='Mes a predecir',
        choices=MESES_CHOICES,
        help_text='Solo el proximo mes o meses anteriores'
    )
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
        help_text='Ingrese un valor entre 1 y 100',
        initial=5
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
    
    def clean_periodosConsiderados(self):
        periodos = self.cleaned_data.get('periodosConsiderados')
        if periodos <= 0:
            raise forms.ValidationError("El número de periodos debe ser mayor que cero.")
        return periodos
    
    def __init__(self, *args, **kwargs):
        super(PromedioMovilPonderadoForm, self).__init__(*args, **kwargs)
        mes_actual = datetime.now().month
        self.fields['mes_a_predecir'].choices = [
            (mes, nombre) for mes, nombre in MESES_CHOICES if mes <= mes_actual + 1
        ]

class SuavizacionExponencialForm(forms.Form):
    prediccionDemanda = forms.IntegerField(label=f'Predicción Demanda de Periodo Anterior ({obtener_nombre_mes(datetime.now().month-1)})',min_value=0,)
    coefSuavizacion = forms.DecimalField(label='Coeficiente de Suavización',min_value=0.0,max_value=1.0,initial=0.05)
    metodoError = forms.ChoiceField(
        label='Método de error a usar',
        choices=ErrorType.choices,
        initial=ErrorType.MAD
    )
    errorAceptable = forms.IntegerField(
        label='Error Aceptable (%)',
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Ingrese un valor entre 1 y 100',
        initial=5
    )
    
    
#Formulario CGI
class ModeloLoteFijoForm(forms.Form):
    demandaAnual = forms.IntegerField(label='Demanda Anual',min_value=0)
    diasLaboralesAnual = forms.IntegerField(label='Dias Laborales Anual',min_value=0)
    

class ModeloIntervaloFijoForm(forms.Form):
    demandaAnual = forms.IntegerField(label='Demanda Anual',min_value=0)
    diasLaboralesAnual = forms.IntegerField(label='Dias Laborales Anual',min_value=0)
    tasaProduccionAnual = forms.IntegerField(label='Tasa de Produccion Anual ',min_value=0)
    costoOrdenProduccion= forms.IntegerField(label='Costo Orden Produccion',min_value=0)
    