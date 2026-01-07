from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)
from django.forms import modelformset_factory
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .utils import login_requerido
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy


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
    success_url = reverse_lazy('escritorio')

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

@method_decorator(login_requerido, name='dispatch')
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = AgregarForm
    template_name = 'MarketPlace/actualizar_producto_simple.html'
    success_url = reverse_lazy('escritorio')
    
    def get_queryset(self):
        usuario_id = self.request.session.get('usuario_id')
        if usuario_id:
            return Producto.objects.filter(id_usuario_id=usuario_id)
        return Producto.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imagenes'] = ImagenProducto.objects.filter(id_producto=self.object)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        # Verificar si se solicita eliminar imágenes
        if 'eliminar_imagen' in request.POST:
            imagen_id = request.POST.get('eliminar_imagen')
            try:
                imagen = ImagenProducto.objects.get(
                    id_imagen=imagen_id,
                    id_producto=self.object
                )
                imagen.delete()
                messages.success(request, 'Imagen eliminada correctamente.')
                return redirect('actualizar_producto', pk=self.object.pk)
            except ImagenProducto.DoesNotExist:
                messages.error(request, 'Imagen no encontrada.')
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado correctamente.')
        return super().form_valid(form)

1
@method_decorator(login_requerido, name='dispatch')
class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'MarketPlace/confirmar_eliminar.html'
    
    def get_success_url(self):
        return reverse_lazy('escritorio')
    
    def get_queryset(self):
        usuario_id = self.request.session.get('usuario_id')
        if usuario_id:
            return Producto.objects.filter(id_usuario_id=usuario_id)
        return Producto.objects.none()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Producto eliminado correctamente.')
        return super().delete(request, *args, **kwargs)
    
@method_decorator(login_requerido, name='dispatch')
class PerfilUpdateView(UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'MarketPlace/perfil.html'
    success_url = reverse_lazy('perfil')
    
    def get_object(self, queryset=None):
        usuario_id = self.request.session.get('usuario_id')
        return get_object_or_404(Usuario, id_usuario=usuario_id)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ocultar algunos campos que no deben editarse desde el perfil
        if 'rol' in form.fields:
            form.fields['rol'].widget = forms.HiddenInput()
        if 'password' in form.fields:
            form.fields['password'].help_text = 'Dejar en blanco para no cambiar la contraseña'
            form.fields['password'].required = False
        return form
    
    def form_valid(self, form):
        password = form.cleaned_data.get('password')
        if password:
            # Encriptar la nueva contraseña
            usuario = form.save(commit=False)
            usuario.set_password(password)
            usuario.save()
            messages.success(self.request, 'Perfil actualizado correctamente. La contraseña ha sido cambiada.')
        else:
            # Guardar sin cambiar la contraseña
            form.save()
            messages.success(self.request, 'Perfil actualizado correctamente.')
        
        # Actualizar el nombre en la sesión si cambió
        if 'nombre' in form.changed_data:
            self.request.session['usuario_nombre'] = form.cleaned_data['nombre']
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.get_object()
        
        # Estadísticas del usuario
        productos_count = Producto.objects.filter(id_usuario=usuario).count()
        productos_activos = Producto.objects.filter(
            id_usuario=usuario, 
            estado='disponible'
        ).count()
        
        context.update({
            'productos_count': productos_count,
            'productos_activos': productos_activos,
            'usuario_info': usuario,
        })
        return context
    
