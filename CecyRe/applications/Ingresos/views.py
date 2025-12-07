from django.shortcuts import render
from django. views.generic import (
    CreateView,
    DetailView,
    ListView,
    )
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


class VentaInternaCLAS(CreateView):
    model = OrdenVenta
    template_name = "Ingresos/ventas_internas.html"
    fields=('__all__')

class VentaExternaCLAS(CreateView):
    model = VentaExterna
    template_name = "Ingresos/ventas_externas.html"
    fields=('__all__') 

class GastosCLAS(CreateView):
    model = Gastos
    template_name = "Ingresos/registro_gasto.html"
    fields=('__all__')

class ReportesCLAS(ListView):
    model = Gastos
    template_name = "Ingresos/generar_reportes.html"
    fields=('__all__')
