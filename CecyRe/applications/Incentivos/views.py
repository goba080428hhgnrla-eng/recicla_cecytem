from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
import uuid
from datetime import datetime

from .models import Recolector, Entrega, Recompensa, Canje, DetalleEntrega, MaterialValor, Rango

# ========== AUTHENTICATION VIEWS ==========

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
                messages.info(request, 'Tu cuenta no está asociada a un recolector. Contacta al administrador.')
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
                else:
                    messages.error(request, 'Error al autenticar el usuario.')
                    
            except Exception as e:
                messages.error(request, f'Error al crear la cuenta: {str(e)}')
        
        return render(request, 'Incentivos/registro.html', {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        })
    
    return render(request, 'Incentivos/registro.html')

# ========== HELPER FUNCTIONS ==========

def actualizar_rango_recolector(recolector):
    """Actualiza el rango del recolector basado en puntos"""
    try:
        nuevo_rango = Rango.objects.filter(
            puntos_minimos__lte=recolector.puntos_acumulados,
            puntos_maximos__gte=recolector.puntos_acumulados
        ).first()
        
        if nuevo_rango and recolector.rango_actual != nuevo_rango:
            recolector.rango_actual = nuevo_rango
            recolector.save()
            return True
    except Exception as e:
        print(f"Error actualizando rango: {e}")
    
    return False

# ========== MAIN PAGES VIEWS ==========

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
        context = {
            'error': 'No tienes un perfil de recolector asociado. Contacta al administrador.'
        }
    
    return render(request, 'Incentivos/dashboard.html', context)

@login_required
def recompensas(request):
    """Página de recompensas disponibles - VERSIÓN CORREGIDA"""
    print(f"DEBUG: Usuario accediendo a recompensas: {request.user.username}")
    
    # OBTENER O CREAR RECOLECTOR (igual que en dashboard)
    try:
        recolector = Recolector.objects.get(usuario=request.user)
    except Recolector.DoesNotExist:
        # Si no existe, crea uno
        import uuid
        codigo_qr = f"REC-{request.user.username.upper()}-{str(uuid.uuid4())[:8]}"
        recolector = Recolector.objects.create(
            usuario=request.user,
            codigo_qr=codigo_qr,
            puntos_acumulados=0
        )
        print(f"DEBUG: Recolector creado: {codigo_qr}")
    
    print(f"DEBUG: Puntos del recolector: {recolector.puntos_acumulados}")
    
    # OBTENER RECOMPENSAS ACTIVAS
    recompensas_lista = Recompensa.objects.filter(activo=True, stock__gt=0).order_by('costo_puntos')
    print(f"DEBUG: Recompensas encontradas: {recompensas_lista.count()}")
    
    # DEBUG: Mostrar cada recompensa
    for r in recompensas_lista:
        print(f"  - {r.id}: {r.nombre} - {r.costo_puntos} pts (Stock: {r.stock})")
    
    context = {
        'recompensas': recompensas_lista,
        'puntos_disponibles': recolector.puntos_acumulados,
        'recolector': recolector  # Por si el template lo necesita
    }
    
    return render(request, 'Incentivos/recompensas.html', context)

@login_required
def perfil(request):
    """Página de perfil del usuario"""
    try:
        recolector = Recolector.objects.get(usuario=request.user)
        canjes = Canje.objects.filter(recolector=recolector).order_by('-fecha_canje')[:10]
        entregas_recientes = Entrega.objects.filter(recolector=recolector).order_by('-fecha_hora_entrega')[:5]
        
        return render(request, 'Incentivos/perfil.html', {
            'recolector': recolector,
            'canjes': canjes,
            'entregas_recientes': entregas_recientes,
            'user': request.user
        })
    except Recolector.DoesNotExist:
        return render(request, 'Incentivos/perfil.html', {
            'error': 'No tienes un perfil de recolector.'
        })

# ========== ACTION VIEWS ==========

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
                
                actualizar_rango_recolector(recolector)
                
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

    