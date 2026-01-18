from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
import uuid

from .models import Recolector, Entrega, Recompensa, Canje, DetalleEntrega, MaterialValor, Rango, CategoriaRecompensa

# vistas de autentificacion

def login_personalizado(request):
    """Vista personalizada para login"""
    if request.user.is_authenticated:
        return redirect('Incentivos:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Por favor ingresa usuario y contraseña.')
            return render(request, 'Incentivos/login.html')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a {username}!')
            
            try:
                Recolector.objects.get(usuario=user)
                return redirect('Incentivos:dashboard')
            except Recolector.DoesNotExist:
                messages.info(request, 'Tu cuenta no está asociada a un recolector.')
                return redirect('/admin/')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'Incentivos/login.html')

def logout_personalizado(request):
    """Vista personalizada para logout"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('Incentivos:login')

def registro(request):
    """Vista para registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('Incentivos:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        errors = []
        
        if not username:
            errors.append('El nombre de usuario es obligatorio.')
        if not email:
            errors.append('El correo electrónico es obligatorio.')
        if not password1:
            errors.append('La contraseña es obligatoria.')
        if password1 != password2:
            errors.append('Las contraseñas no coinciden.')
        if User.objects.filter(username=username).exists():
            errors.append('Este nombre de usuario ya está registrado.')
        if User.objects.filter(email=email).exists():
            errors.append('Este correo electrónico ya está registrado.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                
                codigo_qr = f"REC-{username.upper()}-{str(uuid.uuid4())[:8]}"
                Recolector.objects.create(
                    usuario=user,
                    codigo_qr=codigo_qr,
                    puntos_acumulados=0
                )
                
                user = authenticate(username=username, password=password1)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'¡Cuenta creada exitosamente! Tu código QR es: {codigo_qr}')
                    return redirect('Incentivos:dashboard')
                    
            except Exception as e:
                messages.error(request, f'Error al crear la cuenta: {str(e)}')
        
        return render(request, 'Incentivos/registro.html', {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        })
    
    return render(request, 'Incentivos/registro.html')

# vustas de inicio

def index(request):
    """Página de prueba/inicio"""
    return HttpResponse("¡Módulo de Incentivos funcionando correctamente!")

@login_required
def dashboard(request):
    """Dashboard principal del usuario"""
    try:
        recolector = Recolector.objects.get(usuario=request.user)
        entregas = Entrega.objects.filter(recolector=recolector).order_by('-fecha_hora_entrega')[:10]
        
        recompensas_disponibles = Recompensa.objects.filter(
            activo=True, 
            stock__gt=0, 
            costo_puntos__lte=recolector.puntos_acumulados
        )[:5]
        
        canjes_pendientes = Canje.objects.filter(
            recolector=recolector, 
            estado='pendiente'
        ).count()
        
        context = {
            'recolector': recolector,
            'entregas': entregas,
            'total_entregas': entregas.count(),
            'puntos_totales': recolector.puntos_acumulados,
            'recompensas_disponibles': recompensas_disponibles,
            'canjes_pendientes': canjes_pendientes,
        }
    except Recolector.DoesNotExist:
        context = {'error': 'No tienes un perfil de recolector asociado.'}
    
    return render(request, 'Incentivos/dashboard.html', context)

@login_required
def recompensas(request):
    """Página de recompensas disponibles CON PAGINACIÓN Y FILTROS"""
    try:
        recolector = Recolector.objects.get(usuario=request.user)
    except Recolector.DoesNotExist:
        codigo_qr = f"REC-{request.user.username.upper()}-{str(uuid.uuid4())[:8]}"
        recolector = Recolector.objects.create(
            usuario=request.user,
            codigo_qr=codigo_qr,
            puntos_acumulados=0
        )
    
    # FILTROS
    recompensas_lista = Recompensa.objects.filter(activo=True, stock__gt=0)
    
    # Búsqueda
    busqueda = request.GET.get('q')
    if busqueda:
        recompensas_lista = recompensas_lista.filter(
            Q(nombre__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )
    
    # Orden
    orden = request.GET.get('orden')
    if orden in ['nombre', 'costo_puntos', '-costo_puntos', 'fecha_creacion', '-fecha_creacion']:
        recompensas_lista = recompensas_lista.order_by(orden)
    else:
        recompensas_lista = recompensas_lista.order_by('costo_puntos')
    
    # Filtro por stock
    stock = request.GET.get('stock')
    if stock == 'ultimas':
        recompensas_lista = recompensas_lista.filter(stock__lte=3)
    elif stock == 'disponible':
        recompensas_lista = recompensas_lista.filter(stock__gt=0)
    
    # PAGINACIÓN
    paginator = Paginator(recompensas_lista, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'puntos_disponibles': recolector.puntos_acumulados,
        'recolector': recolector,
        'busqueda_actual': busqueda or '',
        'orden_actual': orden or '',
        'stock_actual': stock or '',
    }
    
    return render(request, 'Incentivos/recompensas.html', context)

@login_required
def perfil(request):
    """Página de perfil del usuario"""
    try:
        recolector = Recolector.objects.get(usuario=request.user)
        canjes = Canje.objects.filter(recolector=recolector).order_by('-fecha_canje')[:10]
        
        return render(request, 'Incentivos/perfil.html', {
            'recolector': recolector,
            'canjes': canjes,
            'user': request.user
        })
    except Recolector.DoesNotExist:
        return render(request, 'Incentivos/perfil.html', {
            'error': 'No tienes un perfil de recolector.'
        })

# vistas de las acciones

@login_required
def canjear_recompensa(request, recompensa_id):
    """Canjear una recompensa por puntos"""
    recolector = get_object_or_404(Recolector, usuario=request.user)
    recompensa = get_object_or_404(Recompensa, id=recompensa_id, activo=True, stock__gt=0)
    
    if recolector.puntos_acumulados < recompensa.costo_puntos:
        messages.error(request, 'No tienes suficientes puntos para canjear esta recompensa.')
        return redirect('Incentivos:recompensas')
    
    try:
        with transaction.atomic():
            canje = Canje.objects.create(
                recolector=recolector,
                recompensa=recompensa,
                puntos_gastados=recompensa.costo_puntos,
                estado='pendiente',
                codigo_retiro=f"CANJE-{str(uuid.uuid4())[:10].upper()}"
            )
            
            recolector.puntos_acumulados -= recompensa.costo_puntos
            recolector.save()
            
            recompensa.stock -= 1
            recompensa.save()
            
            messages.success(request, f'¡Recompensa "{recompensa.nombre}" canjeada exitosamente! Código: {canje.codigo_retiro}')
        
    except Exception as e:
        messages.error(request, f'Error al procesar el canje: {str(e)}')
    
    return redirect('Incentivos:perfil')

@login_required
def nueva_entrega(request):
    """Vista para registrar una nueva entrega"""
    if request.method == 'POST':
        try:
            recolector = Recolector.objects.get(usuario=request.user)
            
            material_id = request.POST.get('material')
            peso_kg = request.POST.get('peso_kg')
            
            if not material_id or not peso_kg:
                messages.error(request, 'Por favor completa todos los campos.')
                return redirect('Incentivos:nueva_entrega')
            
            material = MaterialValor.objects.get(id=material_id, activo=True)
            puntos = int(float(peso_kg) * float(material.puntos_por_kg))
            
            with transaction.atomic():
                entrega = Entrega.objects.create(
                    recolector=recolector,
                    encargado=request.user,
                    total_puntos_obtenidos=puntos,
                    estado='completado'
                )
                
                DetalleEntrega.objects.create(
                    entrega=entrega,
                    material=material,
                    peso_kg=peso_kg,
                    puntos_obtenidos=puntos
                )
                
                recolector.puntos_acumulados += puntos
                recolector.save()
                
                messages.success(request, f'¡Entrega registrada! Ganaste {puntos} puntos.')
                return redirect('Incentivos:dashboard')
                
        except MaterialValor.DoesNotExist:
            messages.error(request, 'Material no válido.')
        except ValueError:
            messages.error(request, 'Peso no válido.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    materiales = MaterialValor.objects.filter(activo=True)
    return render(request, 'Incentivos/nueva_entrega.html', {
        'materiales': materiales
    })

@login_required
def historial(request):
    """Vista para ver historial completo"""
    try:
        recolector = Recolector.objects.get(usuario=request.user)
        
        entregas = Entrega.objects.filter(recolector=recolector).order_by('-fecha_hora_entrega')
        canjes = Canje.objects.filter(recolector=recolector).order_by('-fecha_canje')
        
        total_puntos_ganados = sum(e.total_puntos_obtenidos for e in entregas)
        total_puntos_gastados = sum(c.puntos_gastados for c in canjes)
        
        return render(request, 'Incentivos/historial.html', {
            'recolector': recolector,
            'entregas': entregas,
            'canjes': canjes,
            'total_puntos_ganados': total_puntos_ganados,
            'total_puntos_gastados': total_puntos_gastados,
        })
    except Recolector.DoesNotExist:
        messages.error(request, 'No tienes un perfil de recolector.')
        return redirect('Incentivos:dashboard')