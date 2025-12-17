from django.urls import path
from . import views 

urlpatterns = [
    path('venta-interna/', views.VentaInternaCLAS.as_view(), name='ventainterna'),
    path('dashadmin/', views.DashAdminCLAS.as_view(), name='dashboardadmin'),
    path('venta-externa/', views.VentaExternaCLAS.as_view(), name='ventaexterna'),
    path('registro-gasto/', views.GastosCLAS.as_view(), name='registrogasto'),
    path('generar-reportes/', views.ReportesCLAS.as_view(), name='genreportes'),



]
