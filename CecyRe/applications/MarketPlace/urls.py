from django.urls import path
from . import views 
from .views import ProductoDetailView

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.CrearUsuario.as_view(), name='registro'),
    path('agregar_producto/', views.AgregarProducto.as_view(), name='agregar_producto'),
    path('producto/<int:pk>/', ProductoDetailView.as_view(), name='producto_detail'),
    #path('productos/', views.productos_list, name="productos_list"),
]
