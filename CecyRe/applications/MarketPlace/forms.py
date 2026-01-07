from django import forms
from .models import *
from .models import *

class UsuarioForm(forms.ModelForm):
    
    class Meta:
        model=Usuario
        fields=('__all__') 

class AgregarForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ['id_usuario']  

        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class ImagenProductoForm(forms.ModelForm):
    class Meta:
        model = ImagenProducto
        fields = ('imagen',)  
        widgets = {
            'orden': forms.NumberInput(attrs={'min': 1})
        }