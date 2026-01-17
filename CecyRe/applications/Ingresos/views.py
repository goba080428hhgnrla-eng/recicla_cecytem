from decimal import Decimal
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import date
from .models import Gastos, Producto, VentaExterna, CategoriaGasto
from django.urls import reverse_lazy
from .forms import VentaExternaCLAS, GastosClass

from django. views.generic import (
    CreateView,
    DetailView,
    ListView,
    )
# meses en español
# Diccionario para traducir meses a español
MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo',
    4: 'Abril', 5: 'Mayo', 6: 'Junio',
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre',
    10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}


# Create your views here.

from .models import (
    OrdenVenta,
    VentaExterna,
    DetalleVentaExterna,
    Gastos,
)

class DashAdminCLAS(CreateView):
    model = OrdenVenta
    template_name = "Ingresos/admininicio.html"
    fields=('__all__')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ===== Datos reales para gráfico =====
        gastos_qs = Gastos.objects.annotate(
            mes=TruncMonth('fecha')
        ).values('mes').annotate(total_monto=Sum('monto')).order_by('mes')

        # Rango de meses
        if gastos_qs.exists():
            primer_mes = gastos_qs.first()['mes'].replace(day=1)
            ultimo_mes = gastos_qs.last()['mes'].replace(day=1)
        else:
            hoy = date.today().replace(day=1)
            primer_mes = date(hoy.year, max(hoy.month - 5, 1), 1)  # últimos 6 meses
            ultimo_mes = hoy

        # Lista de todos los meses consecutivos
        meses_lista = []
        current = primer_mes
        while current <= ultimo_mes:
            meses_lista.append(current)
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        # Diccionario de montos por mes
        montos_dict = {g['mes'].replace(day=1): float(g['total_monto']) for g in gastos_qs}

        # Crear listas finales para Chart.js
        context['meses'] = [f"{MESES_ES[m.month]} {m.year}" for m in meses_lista]
        context['montos'] = [montos_dict.get(m, 0) for m in meses_lista]
        # Total de gastos
        total_gastos = Gastos.objects.aggregate(total=Sum('monto'))['total'] or 0
        context['total_gastos'] = total_gastos
           # ===== TOTAL VENTAS EXTERNAS =====
        total_ventas_externas = VentaExterna.objects.aggregate(
         total=Sum('total')
           )['total'] or Decimal('0.00')

        context['total_ventas_externas'] = total_ventas_externas
        # 🔹 Productos disponibles
        productos_disponibles = Producto.objects.filter(
        estado='disponible',
        peso_disponible_kg__gt=0
         ).count()

        context['productos_disponibles'] = productos_disponibles

          # Últimas 5 ventas externas
        ventas = VentaExterna.objects.all().order_by('-fecha')[:4]

         # Últimos 5 gastos
        gastos = Gastos.objects.all().order_by('-fecha')[:4]

        context['ventas_recientes'] = ventas
        context['gastos_recientes'] = gastos

           # ===== Datos para gráfico circular =====
        gastos_por_categoria = (
            Gastos.objects
            .values('id_categoria_gasto__nombre')  # nombre de la categoría
            .annotate(total=Sum('monto'))          # suma de montos
            .order_by('-total')
        )

        # Listas separadas para Chart.js
        context['categorias'] = [g['id_categoria_gasto__nombre'] for g in gastos_por_categoria]
        context['montos_categoria'] = [float(g['total']) for g in gastos_por_categoria]

        return context

class VentaExternaCLAS(FormView):
    template_name = "Ingresos/ventas_externas.html"
    form_class = VentaExternaCLAS
    success_url = reverse_lazy('ventainterna')

    def form_valid(self, form):
        
        usuario = form.cleaned_data['id_usuario']   

        # ====== Guardar Venta Externa ======
        venta = VentaExterna.objects.create(
            descripcion=form.cleaned_data['descripcion'],
            cliente_nombre=form.cleaned_data['cliente_nombre'],
            cliente_contacto=form.cleaned_data['cliente_contacto'],
            total=form.cleaned_data['total'],
            fecha=form.cleaned_data['fecha'],
            id_usuario=usuario 
        )

        # ====== Guardar Detalle relacionado ======
        DetalleVentaExterna.objects.create(
            materia=form.cleaned_data['materia'],
            cantidad_kg=form.cleaned_data['cantidad_kg'],
            precio_kg=form.cleaned_data['precio_kg'],
            subtotal=form.cleaned_data['subtotal'],
            id_venta_externa=venta
        )

        return super().form_valid(form)  # redirección con success_url





# views de gastos
class GastosCLAS(FormView):
    template_name = "Ingresos/registro_gasto.html"
    form_class = GastosClass
    success_url = reverse_lazy('registrogasto')

    def form_valid(self, form):
        data = form.cleaned_data
        Gastos.objects.create(
            concepto=data['concepto'],
            monto=data['monto'],
            fecha=data['fecha'],
            descripcion=data['descripcion'],
            id_categoria_gasto=data['id_categoria_gasto'],
            factura_adjunto=data['factura_adjunto'],
            id_usuario=data['id_usuario'],
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Tabla de últimos 3 gastos
        context['gastos'] = Gastos.objects.all().order_by('-fecha')[:3]

        # ===== Datos reales para gráfico =====
        gastos_qs = Gastos.objects.annotate(
            mes=TruncMonth('fecha')
        ).values('mes').annotate(total_monto=Sum('monto')).order_by('mes')

        # Rango de meses
        if gastos_qs.exists():
            primer_mes = gastos_qs.first()['mes'].replace(day=1)
            ultimo_mes = gastos_qs.last()['mes'].replace(day=1)
        else:
            hoy = date.today().replace(day=1)
            primer_mes = date(hoy.year, max(hoy.month - 5, 1), 1)  # últimos 6 meses
            ultimo_mes = hoy

        # Lista de todos los meses consecutivos
        meses_lista = []
        current = primer_mes
        while current <= ultimo_mes:
            meses_lista.append(current)
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        # Diccionario de montos por mes
        montos_dict = {g['mes'].replace(day=1): float(g['total_monto']) for g in gastos_qs}

        # Crear listas finales para Chart.js
        context['meses'] = [f"{MESES_ES[m.month]} {m.year}" for m in meses_lista]
        context['montos'] = [montos_dict.get(m, 0) for m in meses_lista]

        return context


    
    

class ReportesCLAS(ListView):
    model = Gastos
    template_name = "Ingresos/generar_reportes.html"
    fields=('__all__')
