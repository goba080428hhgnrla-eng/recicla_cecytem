
from django import forms
from .models import *

class RecolectorForm(forms.ModelForm):
    class Meta:
        model = Recolector
        fields = ['usuario', 'codigo_qr']
        widgets = {
            'codigo_qr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dejar vacío para generar automáticamente'
            }),
            'usuario': forms.Select(attrs={'class': 'form-control'}),
        }

class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['recolector']
        widgets = {
            'recolector': forms.Select(attrs={'class': 'form-control'}),
        }

class DetalleEntregaForm(forms.ModelForm):
    class Meta:
        model = DetalleEntrega
        fields = ['material', 'peso_kg']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.1'
            }),
        }

class CanjeForm(forms.ModelForm):
    class Meta:
        model = Canje
        fields = ['recolector', 'recompensa']
        widgets = {
            'recolector': forms.Select(attrs={'class': 'form-control'}),
            'recompensa': forms.Select(attrs={'class': 'form-control'}),
        }
        

class RecompensaForm(forms.ModelForm):
    class Meta:
        model = Recompensa
        fields = ['nombre', 'descripcion', 'categoria', 'costo_puntos', 'stock', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'costo_puntos': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FiltroReporteForm(forms.Form):
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
