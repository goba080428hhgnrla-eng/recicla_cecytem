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
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from decimal import Decimal
import json
import paypalrestsdk
from decimal import Decimal
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')

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

def terminos(request):
    return render(request, "MarketPlace/terminos_condiciones.html")

def politica(request):
    return render(request, "MarketPlace/politica.html")

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
    
@login_requerido
def carrito_view(request):
    """Vista para mostrar el carrito del usuario"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    try:
        carrito = Carrito.objects.get(id_usuario=usuario)
        items = ItemCarrito.objects.filter(id_carrito=carrito).select_related('id_producto')
        
        # Calcular total
        total = sum(item.subtotal for item in items)
    except Carrito.DoesNotExist:
        carrito = None
        items = []
        total = Decimal('0.00')
    
    return render(request, 'MarketPlace/carrito.html', {
        'carrito': carrito,
        'items': items,
        'total': total,
        'usuario': usuario
    })

@require_POST
@login_requerido
def agregar_al_carrito(request, producto_id):
    """Vista para agregar un producto al carrito"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    producto = get_object_or_404(Producto, id_producto=producto_id)
    
    # Verificar que el producto esté disponible
    if producto.estado != 'disponible':
        messages.error(request, 'Este producto no está disponible')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Producto no disponible'})
        return redirect('producto_detail', pk=producto_id)
    
    # Obtener o crear carrito
    carrito, created = Carrito.objects.get_or_create(id_usuario=usuario)
    
    cantidad_kg = Decimal(request.POST.get('cantidad', '1'))
    
    # Validar cantidad
    if cantidad_kg <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Cantidad inválida'})
        messages.error(request, 'Cantidad inválida')
        return redirect('producto_detail', pk=producto_id)
    
    if cantidad_kg > producto.peso_disponible_kg:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Cantidad excede el peso disponible'})
        messages.error(request, 'La cantidad excede el peso disponible')
        return redirect('producto_detail', pk=producto_id)
    
    try:
        with transaction.atomic():
            # Verificar si el producto ya está en el carrito
            item_existente = ItemCarrito.objects.filter(
                id_carrito=carrito,
                id_producto=producto
            ).first()
            
            if item_existente:
                # Si existe, actualizar cantidad
                nueva_cantidad = item_existente.cantidad_kg + cantidad_kg
                
                # Verificar que no exceda el stock
                if nueva_cantidad > producto.peso_disponible_kg:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False, 
                            'error': f'Solo quedan {producto.peso_disponible_kg} kg disponibles'
                        })
                    messages.error(request, f'Solo quedan {producto.peso_disponible_kg} kg disponibles')
                    return redirect('producto_detail', pk=producto_id)
                
                item_existente.cantidad_kg = nueva_cantidad
                item_existente.subtotal = nueva_cantidad * item_existente.precio_unitario
                item_existente.save()
                accion = 'actualizado'
            else:
                # Si no existe, crear nuevo item
                precio_unitario = producto.precio_kg
                subtotal = cantidad_kg * precio_unitario
                
                ItemCarrito.objects.create(
                    id_carrito=carrito,
                    id_producto=producto,
                    cantidad_kg=cantidad_kg,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )
                accion = 'agregado'
            
            # Actualizar conteo del carrito en sesión
            items_count = ItemCarrito.objects.filter(id_carrito=carrito).count()
            request.session['carrito_count'] = items_count
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Producto {accion} al carrito',
                    'carrito_count': items_count
                })
            
            messages.success(request, f'Producto {accion} al carrito exitosamente')
            
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, 'Error al agregar producto al carrito')
    
    # Redirigir según el origen
    next_url = request.POST.get('next', 'carrito')
    if next_url == 'detalle':
        return redirect('producto_detail', pk=producto_id)
    return redirect('carrito')

@require_POST
@login_requerido
def eliminar_del_carrito(request, item_id):
    """Vista para eliminar un item del carrito"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    try:
        carrito = Carrito.objects.get(id_usuario=usuario)
        item = get_object_or_404(ItemCarrito, id_item=item_id, id_carrito=carrito)
        item.delete()
        
        # Actualizar conteo del carrito
        items_count = ItemCarrito.objects.filter(id_carrito=carrito).count()
        request.session['carrito_count'] = items_count
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Producto eliminado del carrito',
                'carrito_count': items_count
            })
        
        messages.success(request, 'Producto eliminado del carrito')
        
    except ItemCarrito.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Item no encontrado'})
        messages.error(request, 'Item no encontrado')
    
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, 'Error al eliminar producto')
    
    return redirect('carrito')

@require_POST
@login_requerido
def actualizar_cantidad_carrito(request, item_id):
    """Vista para actualizar la cantidad de un item en el carrito"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    cantidad = request.POST.get('cantidad')
    if not cantidad:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Cantidad no especificada'})
        messages.error(request, 'Cantidad no especificada')
        return redirect('carrito')
    
    try:
        cantidad_kg = Decimal(cantidad)
        if cantidad_kg <= 0:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Cantidad inválida'})
            messages.error(request, 'Cantidad inválida')
            return redirect('carrito')
        
        carrito = Carrito.objects.get(id_usuario=usuario)
        item = get_object_or_404(ItemCarrito, id_item=item_id, id_carrito=carrito)
        
        # Verificar stock disponible
        if cantidad_kg > item.id_producto.peso_disponible_kg:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': f'Solo hay {item.id_producto.peso_disponible_kg} kg disponibles'
                })
            messages.error(request, f'Solo hay {item.id_producto.peso_disponible_kg} kg disponibles')
            return redirect('carrito')
        
        # Actualizar item
        item.cantidad_kg = cantidad_kg
        item.subtotal = cantidad_kg * item.precio_unitario
        item.save()
        
        # Calcular nuevo total
        items = ItemCarrito.objects.filter(id_carrito=carrito)
        total = sum(item.subtotal for item in items)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'subtotal': str(item.subtotal),
                'total': str(total)
            })
        
        messages.success(request, 'Cantidad actualizada')
        
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, 'Error al actualizar cantidad')
    
    return redirect('carrito')
#Vistas de Finzalizar Compra

@login_requerido
def checkout_view(request):
    """Vista para finalizar compra"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    # Obtener carrito del usuario
    try:
        carrito = Carrito.objects.get(id_usuario=usuario)
        items = ItemCarrito.objects.filter(id_carrito=carrito).select_related('id_producto')
        
        if not items:
            messages.error(request, 'Tu carrito está vacío')
            return redirect('carrito')
        
        # Verificar disponibilidad
        for item in items:
            if item.cantidad_kg > item.id_producto.peso_disponible_kg:
                messages.error(
                    request, 
                    f'El producto {item.id_producto.nombre} no tiene suficiente stock'
                )
                return redirect('carrito')
        
        # Calcular total
        total = sum(item.subtotal for item in items)
        
        # Métodos de pago disponibles
        metodos_pago = [
            {'id': 'paypal', 'nombre': 'PayPal', 'icono': 'fab fa-paypal'},
            {'id': 'tarjeta', 'nombre': 'Tarjeta de Crédito/Débito', 'icono': 'fas fa-credit-card'},
        ]
        
        return render(request, 'MarketPlace/checkout.html', {
            'usuario': usuario,
            'items': items,
            'total': total,
            'metodos_pago': metodos_pago,
            'carrito': carrito,
        })
        
    except Carrito.DoesNotExist:
        messages.error(request, 'Tu carrito está vacío')
        return redirect('carrito')

@login_requerido
@require_POST
def crear_orden(request):
    """Crear orden de venta a partir del carrito"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    metodo_pago = request.POST.get('metodo_pago')
    
    if not metodo_pago:
        messages.error(request, 'Debes seleccionar un método de pago')
        return redirect('checkout')
    
    try:
        with transaction.atomic():
            # Obtener carrito y items
            carrito = Carrito.objects.get(id_usuario=usuario)
            items = ItemCarrito.objects.filter(id_carrito=carrito).select_related('id_producto')
            
            if not items:
                messages.error(request, 'Tu carrito está vacío')
                return redirect('carrito')
            
            # Calcular total y verificar stock
            total = Decimal('0.00')
            productos_por_vendedor = {}
            
            for item in items:
                # Agrupar productos por vendedor
                vendedor_id = item.id_producto.id_usuario.id_usuario
                if vendedor_id not in productos_por_vendedor:
                    productos_por_vendedor[vendedor_id] = []
                productos_por_vendedor[vendedor_id].append(item)
                
                total += item.subtotal
            
            # Crear una orden por cada vendedor
            ordenes_creadas = []
            
            for vendedor_id, items_vendedor in productos_por_vendedor.items():
                vendedor = Usuario.objects.get(id_usuario=vendedor_id)
                
                # Crear orden de venta
                orden = OrdenVenta.objects.create(
                    id_usuario_vendedor=vendedor,
                    id_usuario_comprador=usuario,
                    total=sum(item.subtotal for item in items_vendedor),
                    estado_orden='pendiente'
                )
                
                # Crear detalles de orden y actualizar stock
                for item in items_vendedor:
                    DetalleOrden.objects.create(
                        id_orden=orden,
                        id_producto=item.id_producto,
                        cantidad_kg=item.cantidad_kg,
                        precio_unitario=item.precio_unitario,
                        subtotal=item.subtotal
                    )
                    
                    # Actualizar stock del producto
                    producto = item.id_producto
                    producto.peso_disponible_kg -= item.cantidad_kg
                    if producto.peso_disponible_kg <= 0:
                        producto.estado = 'no_disponible'
                    producto.save()
                
                # Crear registro de pago pendiente
                Pago.objects.create(
                    id_orden=orden,
                    metodo_pago=metodo_pago,
                    monto=orden.total,
                    estado_pago='pendiente'
                )
                
                ordenes_creadas.append(orden)
            
            # Vaciar carrito
            items.delete()
            request.session['carrito_count'] = 0
            
            # Redirigir según método de pago
            if metodo_pago == 'paypal':
                # Crear pago PayPal para la primera orden (podrías modificar para múltiples)
                if ordenes_creadas:
                    return redirect('crear_pago_paypal', orden_id=ordenes_creadas[0].id_orden)
            elif metodo_pago == 'tarjeta':
                # Procesar tarjeta (Stripe o otro)
                return redirect('procesar_tarjeta', orden_id=ordenes_creadas[0].id_orden)
            
            messages.success(request, 'Orden creada exitosamente')
            return redirect('ordenes_usuario')
            
    except Exception as e:
        messages.error(request, f'Error al crear la orden: {str(e)}')
        return redirect('checkout')

@login_requerido
def crear_pago_paypal(request, orden_id):
    """Crear pago de PayPal"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    orden = get_object_or_404(OrdenVenta, id_orden=orden_id, id_usuario_comprador=usuario)
    
    try:
        # Configurar el pago de PayPal
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(f'/pago/paypal/ejecutar/{orden.id_orden}/'),
                "cancel_url": request.build_absolute_uri('/pago/paypal/cancelado/')
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Orden #{orden.id_orden}",
                        "sku": f"ORDEN-{orden.id_orden}",
                        "price": str(orden.total),
                        "currency": "MXN",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(orden.total),
                    "currency": "MXN"
                },
                "description": f"Compra de productos reciclables - Orden {orden.id_orden}"
            }]
        })
        
        if payment.create():
            # Guardar ID del pago de PayPal en la base de datos
            pago = Pago.objects.get(id_orden=orden)
            pago.paypal_payment_id = payment.id
            pago.referencia_pago = f"PAYPAL-{payment.id}"
            pago.save()
            
            # Redirigir a PayPal
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    return redirect(approval_url)
        else:
            messages.error(request, f'Error al crear pago PayPal: {payment.error}')
            return redirect('checkout')
            
    except Exception as e:
        messages.error(request, f'Error al procesar pago PayPal: {str(e)}')
        return redirect('checkout')

@login_requerido
def ejecutar_pago_paypal(request, orden_id):
    """Ejecutar pago de PayPal después de la aprobación"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    orden = get_object_or_404(OrdenVenta, id_orden=orden_id, id_usuario_comprador=usuario)
    
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    if not payment_id or not payer_id:
        messages.error(request, 'Faltan parámetros del pago')
        return redirect('checkout')
    
    try:
        # Buscar pago existente
        pago = Pago.objects.get(id_orden=orden)
        
        if pago.estado_pago == 'completado':
            messages.info(request, 'Este pago ya fue procesado')
            return redirect('detalle_orden', orden_id=orden.id_orden)
        
        # Ejecutar el pago
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Actualizar estado del pago
            pago.estado_pago = 'completado'
            pago.transaccion_id = payment.transactions[0].related_resources[0].sale.id
            pago.paypal_payer_id = payer_id
            pago.datos_pago = {
                'estado': payment.state,
                'create_time': payment.create_time,
                'update_time': payment.update_time,
                'transaccion': payment.transactions[0].to_dict()
            }
            pago.save()
            
            # Actualizar estado de la orden
            orden.estado_orden = 'completada'
            orden.save()
            
            messages.success(request, '¡Pago completado exitosamente!')
            return redirect('detalle_orden', orden_id=orden.id_orden)
        else:
            messages.error(request, f'Error al ejecutar pago: {payment.error}')
            pago.estado_pago = 'fallido'
            pago.save()
            return redirect('checkout')
            
    except Exception as e:
        messages.error(request, f'Error al procesar pago: {str(e)}')
        return redirect('checkout')

@login_requerido
def pago_paypal_cancelado(request):
    """Vista para cuando se cancela el pago de PayPal"""
    messages.warning(request, 'El pago fue cancelado')
    return redirect('checkout')

@login_requerido
def procesar_tarjeta(request, orden_id):
    """Vista para procesar pago con tarjeta"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    orden = get_object_or_404(OrdenVenta, id_orden=orden_id, id_usuario_comprador=usuario)
    
    if request.method == 'POST':
        # Aquí integrarías con Stripe u otra pasarela
        # Por ahora, simularemos un pago exitoso
        try:
            # Simular procesamiento de tarjeta
            numero_tarjeta = request.POST.get('numero_tarjeta')
            fecha_expiracion = request.POST.get('fecha_expiracion')
            cvv = request.POST.get('cvv')
            
            # Validaciones básicas (en producción usaría una biblioteca segura)
            if not (numero_tarjeta and fecha_expiracion and cvv):
                messages.error(request, 'Por favor completa todos los campos')
                return render(request, 'MarketPlace/pago_tarjeta.html', {'orden': orden})
            
            # Aquí iría la integración real con Stripe
            # stripe.Charge.create(...)
            
            # Simular pago exitoso
            pago = Pago.objects.get(id_orden=orden)
            pago.estado_pago = 'completado'
            pago.transaccion_id = f"TARJ-{orden.id_orden}-{pago.id_pago}"
            pago.referencia_pago = f"Tarjeta terminada en {numero_tarjeta[-4:]}"
            pago.save()
            
            # Actualizar orden
            orden.estado_orden = 'completada'
            orden.save()
            
            messages.success(request, '¡Pago con tarjeta completado exitosamente!')
            return redirect('detalle_orden', orden_id=orden.id_orden)
            
        except Exception as e:
            messages.error(request, f'Error al procesar tarjeta: {str(e)}')
            return redirect('checkout')
    
    return render(request, 'MarketPlace/pago_tarjeta.html', {
        'orden': orden,
        'usuario': usuario,
    })

@login_requerido
def ordenes_usuario(request):
    """Vista para ver órdenes del usuario"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    # Órdenes como comprador
    ordenes_compra = OrdenVenta.objects.filter(id_usuario_comprador=usuario).order_by('-fecha')
    # Órdenes como vendedor
    ordenes_venta = OrdenVenta.objects.filter(id_usuario_vendedor=usuario).order_by('-fecha')
    
    return render(request, 'MarketPlace/ordenes.html', {
        'usuario': usuario,
        'ordenes_compra': ordenes_compra,
        'ordenes_venta': ordenes_venta,
    })

@login_requerido
def detalle_orden(request, orden_id):
    """Vista para ver detalle de una orden"""
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    orden = get_object_or_404(
        OrdenVenta, 
        id_orden=orden_id,
        id_usuario_comprador=usuario
    )
    
    detalles = DetalleOrden.objects.filter(id_orden=orden).select_related('id_producto')
    pago = Pago.objects.filter(id_orden=orden).first()
    
    return render(request, 'MarketPlace/detalle_orden.html', {
        'orden': orden,
        'detalles': detalles,
        'pago': pago,
        'usuario': usuario,
    })
    

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def buscar_productos(request):
    """Vista para buscar productos con filtros"""
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    pureza = request.GET.get('pureza', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    estado = request.GET.get('estado', 'disponible')
    ordenar_por = request.GET.get('ordenar_por', 'recientes')
    
    # Obtener todos los productos inicialmente
    productos = Producto.objects.filter(estado='disponible')
    
    # Aplicar búsqueda por texto
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(id_categoria__nombre__icontains=query)
        )
    
    # Aplicar filtros
    if categoria_id:
        productos = productos.filter(id_categoria_id=categoria_id)
    
    if pureza:
        productos = productos.filter(pureza=pureza)
    
    if precio_min:
        try:
            productos = productos.filter(precio_kg__gte=float(precio_min))
        except ValueError:
            pass
    
    if precio_max:
        try:
            productos = productos.filter(precio_kg__lte=float(precio_max))
        except ValueError:
            pass
    
    if estado:
        productos = productos.filter(estado=estado)
    
    # Aplicar ordenamiento
    if ordenar_por == 'precio_asc':
        productos = productos.order_by('precio_kg')
    elif ordenar_por == 'precio_desc':
        productos = productos.order_by('-precio_kg')
    elif ordenar_por == 'nombre':
        productos = productos.order_by('nombre')
    elif ordenar_por == 'peso':
        productos = productos.order_by('-peso_disponible_kg')
    else:  # recientes por defecto
        productos = productos.order_by('-fecha_publicacion')
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(productos, 12)  # 12 productos por página
    
    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)
    
    # Obtener todas las categorías para el filtro
    categorias = Categoria.objects.all()
    
    context = {
        'productos': productos_paginados,
        'query': query,
        'categorias': categorias,
        'filtros': {
            'categoria_id': categoria_id,
            'pureza': pureza,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'estado': estado,
            'ordenar_por': ordenar_por,
        },
        'PUREZA_CHOICES': Producto.PUREZA,
        'ESTADO_CHOICES': Producto.ESTADO,
    }
    
    return render(request, 'Marketplace/buscar_productos.html', context)

def home(request):
    """Vista principal con opción de mostrar todos los productos o filtrados"""
    productos = Producto.objects.filter(estado='disponible').order_by('-fecha_publicacion')
    
    # Si hay parámetros de filtro, mostrar productos filtrados
    if any([request.GET.get(key) for key in ['q', 'categoria', 'pureza', 'precio_min', 'precio_max']]):
        return buscar_productos(request)
    
    # Paginación para la página principal
    page = request.GET.get('page', 1)
    paginator = Paginator(productos, 12)
    
    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)
    
    # Obtener categorías para sidebar
    categorias = Categoria.objects.all()
    
    return render(request, "MarketPlace/home.html", {
        'productos': productos_paginados,
        'categorias': categorias,
        'PUREZA_CHOICES': Producto.PUREZA,
    })
