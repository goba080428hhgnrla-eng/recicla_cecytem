from django.shortcuts import render
from .models import *
from .forms import *
from django. views.generic import (
    CreateView,
    DetailView
    )
from django.forms import modelformset_factory
from django.shortcuts import redirect

def home(request):
    productos = Producto.objects.all()
    return render(request, 'MarketPlace/home.html', {
        'productos': productos
    })


class CrearUsuario(CreateView):
    model=Usuario
    form_class= UsuarioForm
    template_name='Marketplace/usuario.html'
    success_url='success_url'

class AgregarProducto(CreateView):
    model = Producto
    form_class = AgregarForm
    template_name = 'Marketplace/agregar_producto.html'
    success_url = '/productos/'  

    def get(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        ImagenFormSet = modelformset_factory(ImagenProducto, form=ImagenProductoForm, extra=2)
        formset = ImagenFormSet(queryset=ImagenProducto.objects.none())

        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        ImagenFormSet = modelformset_factory(ImagenProducto, form=ImagenProductoForm, extra=2)
        formset = ImagenFormSet(request.POST, request.FILES, queryset=ImagenProducto.objects.none())

        if form.is_valid() and formset.is_valid():
            producto = form.save()

            for img_form in formset:
                if img_form.cleaned_data:
                    imagen = img_form.save(commit=False)
                    imagen.id_producto = producto
                    imagen.save()

            return redirect(self.success_url)

        return self.render_to_response(self.get_context_data(form=form, formset=formset))
    
class ProductoDetailView(DetailView):
    model = Producto
    template_name = "Marketplace/producto_detalle.html"
    context_object_name = "producto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["imagenes"] = ImagenProducto.objects.filter(id_producto=self.object)
        return context


    
# Create your views here.
