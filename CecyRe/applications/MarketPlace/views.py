from django.shortcuts import render
from .models import *
from .forms import *
from django.views.generic import (
    CreateView,
    DetailView
)
from django.forms import modelformset_factory
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Producto, Usuario
from .utils import login_requerido
from django.utils.decorators import method_decorator


def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        password = request.POST.get("password")
        
        usuarios = Usuario.objects.filter(correo=correo)

        if not usuarios.exists():
            messages.error(request, "Correo o contraseña incorrectos")
            return render(request, "Marketplace/login.html")

        usuario = usuarios.first() 

        if check_password(password, usuario.password):
            request.session["usuario_id"] = usuario.id_usuario
            request.session["usuario_nombre"] = usuario.nombre
            request.session["usuario_rol"] = usuario.rol
            return redirect("home")
        else:
            messages.error(request, "Correo o contraseña incorrectos")

    return render(request, "Marketplace/login.html")



def home(request):
    productos = Producto.objects.all()
    return render(request, "MarketPlace/home.html", {'productos': productos})

class CrearUsuario(CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'Marketplace/usuario.html'
    success_url = '/success/'  

@method_decorator(login_requerido, name='dispatch')
class AgregarProducto(CreateView):
    model = Producto
    form_class = AgregarForm
    template_name = 'MarketPlace/agregar_producto.html'
    success_url = '/escritorio/'

    def get_formset(self):
        ImagenFormSet = modelformset_factory(
            ImagenProducto,
            form=ImagenProductoForm,
            extra=2,
            max_num=5
        )

        if self.request.method == "POST":
            return ImagenFormSet(
                self.request.POST,
                self.request.FILES,
                queryset=ImagenProducto.objects.none()
            )
        
        return ImagenFormSet(queryset=ImagenProducto.objects.none())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["formset"] = kwargs.get("formset", self.get_formset())

        return context

    def form_valid(self, form):
        usuario_id = self.request.session.get('usuario_id')
        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
        except Usuario.DoesNotExist:
            messages.error(self.request, "Usuario no encontrado")
            return redirect('login')

        producto = form.save(commit=False)
        producto.id_usuario = usuario
        producto.save()

        formset = self.get_formset()

        if formset.is_valid():
            for i, img_form in enumerate(formset):
                if img_form.cleaned_data:
                    imagen = img_form.save(commit=False)
                    imagen.id_producto = producto
                    imagen.orden = i + 1
                    imagen.save()
        else:
            return self.form_invalid(form, formset=formset)

        messages.success(self.request, "Producto creado exitosamente")
        return redirect(self.success_url)

    def form_invalid(self, form, formset=None):
        print("ERRORES DEL FORMULARIO:", form.errors)
        if formset:
            print("ERRORES DEL FORMSET:", formset.errors)

        if formset is None:
            formset = self.get_formset()

        messages.error(self.request, "Error al crear el producto")
        return self.render_to_response(self.get_context_data(form=form, formset=formset))
    
class ProductoDetailView(DetailView):
    model = Producto
    template_name = "Marketplace/producto_detalle.html"
    context_object_name = "producto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["imagenes"] = ImagenProducto.objects.filter(id_producto=self.object)
        return context

@login_requerido
def escritorio_view(request):
    usuario_id = request.session['usuario_id']
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    productos = Producto.objects.filter(id_usuario=usuario)

    return render(request, 'MarketPlace/escritorio.html', {
        'usuario': usuario,
        'productos': productos,
    })