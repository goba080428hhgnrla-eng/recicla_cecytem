# En utils.py o donde tengas el decorador, actualízalo:
from functools import wraps
from django.shortcuts import redirect

def login_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('login')
        
        if 'usuario_id' in request.session:
            from .models import Carrito, ItemCarrito
            try:
                carrito = Carrito.objects.get(id_usuario_id=request.session['usuario_id'])
                items_count = ItemCarrito.objects.filter(id_carrito=carrito).count()
                request.session['carrito_count'] = items_count
            except Carrito.DoesNotExist:
                request.session['carrito_count'] = 0
        
        return view_func(request, *args, **kwargs)
    return wrapper