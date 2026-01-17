from django.urls import path
from . import views 

urlpatterns = [
 
    path('dashadmin/', views.DashAdminCLAS.as_view(), name='dashboardadmin'),
    path('venta-externa/', views.VentaExternaCLAS.as_view(), name='ventaexterna'),
    path('registro-gasto/', views.GastosCLAS.as_view(), name='registrogasto'),
    path('generar-reportes/', views.ReportesCLAS.as_view(), name='genreportes'),
    path('reporte-gasto/<int:id>/', views.generar_reporte_gasto, name='reporte-gasto'),
    path('reporte-venta/<int:id>/', views.generar_reporte_venta, name='reporte-venta'),
]
