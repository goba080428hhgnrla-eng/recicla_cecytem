from django.urls import path
from . import views  
from .views import AgregarProducto
from .views import ProductoDetailView
from .views import login_view, home, PerfilUpdateView
from .views import *

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.CrearUsuario.as_view(), name='registro'),
    path('iniciar/', views.CrearUsuario.as_view(), name='registro'),
    path('agregar-producto/', views.AgregarProducto.as_view(), name='agregar_producto'),
    path('producto/<int:pk>/', ProductoDetailView.as_view(), name='producto_detail'),
    path('login/', login_view, name='login'),
    path('escritorio/', views.escritorio_view, name='escritorio'),
    path('productos/actualizar/<int:pk>/', 
         views.ProductoUpdateView.as_view(), 
         name='actualizar_producto'),
    path('productos/eliminar/<int:pk>/', 
         views.ProductoDeleteView.as_view(), 
         name='eliminar_producto'),
    #path('productos/', views.productos_list, name="productos_list"),
    path('perfil/', PerfilUpdateView.as_view(), name='perfil'),
    path('carrito/', carrito_view, name='carrito'),
    path('carrito/agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:item_id>/', actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
]
