from django import forms
from .models import *
from .models import *

class UsuarioForm(forms.ModelForm):
    
    class Meta:
        model=Usuario
        fields=('__all__') 

class AgregarForm(forms.ModelForm):
    class Meta:
        model=Producto
        fields=('__all__') 
        
class ImagenProductoForm(forms.ModelForm):
    class Meta:
        model = ImagenProducto
        fields = ('imagen', 'orden')
        widgets = {
            'orden': forms.NumberInput(attrs={'min': 1})
        }