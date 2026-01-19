from django import forms
from .models import Usuario, CategoriaGasto      
# Formulario Venta Externa
class VentaExternaCLAS(forms.Form):
    # --- Tabla VentaExterna ---
    descripcion = forms.CharField(widget=forms.Textarea)
    cliente_nombre = forms.CharField(max_length=50)
    cliente_contacto = forms.IntegerField()
    total = forms.DecimalField(max_digits=10, decimal_places=2)
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    id_usuario = forms.ModelChoiceField(
    queryset=Usuario.objects.all(),
    label="Usuario responsable"
)
    # --- Tabla DetalleVentaExterna ---
    materia = forms.ChoiceField(choices=[
        ('1', 'Plástico'),
        ('2', 'Metal'),
        ('3', 'Papel'),
        ('4', 'Otro')
    ])
    cantidad_kg = forms.DecimalField(max_digits=10, decimal_places=2)
    precio_kg = forms.DecimalField(max_digits=10, decimal_places=2)
# formularios de gastos
class GastosClass(forms.Form):
    concepto = forms.CharField(widget=forms.Textarea)
    monto = forms.DecimalField(max_digits=10, decimal_places=2)
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    descripcion = forms.CharField(widget=forms.Textarea)

    id_categoria_gasto = forms.ModelChoiceField(
    queryset=CategoriaGasto.objects.all(),
    label="Categoria del gasto"
    )


    id_usuario = forms.ModelChoiceField(
    queryset=Usuario.objects.all(),
    label="Usuario responsable"
)


    

    

