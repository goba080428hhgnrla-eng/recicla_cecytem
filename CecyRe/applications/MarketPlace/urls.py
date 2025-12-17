from django.urls import path
from . import views  
from .views import AgregarProducto
from .views import ProductoDetailView
from .views import login_view, home

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.CrearUsuario.as_view(), name='registro'),
    path('iniciar/', views.CrearUsuario.as_view(), name='registro'),
    path('agregar-producto/', views.AgregarProducto.as_view(), name='agregar_producto'),
    path('producto/<int:pk>/', ProductoDetailView.as_view(), name='producto_detail'),
    path('login/', login_view, name='login'),
    path('escritorio/', views.escritorio_view, name='escritorio'),
    #path('productos/', views.productos_list, name="productos_list"),
]
