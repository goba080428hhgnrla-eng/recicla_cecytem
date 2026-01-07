from django.urls import path
from . import views

app_name = 'Incentivos'

urlpatterns = [
    # Página principal del módulo (login)
    path('', views.login_personalizado, name='login'),
    path('login/', views.login_personalizado, name='login'),
    
    # Registro y logout
    path('registro2/', views.registro, name='registro'),
    path('logout/', views.logout_personalizado, name='logout'),
    
    # Dashboard y páginas principales
    path('dashboard/', views.dashboard, name='dashboard'),
    path('recompensas/', views.recompensas, name='recompensas'),
    path('perfil/', views.perfil, name='perfil'),
    
    # Acciones
    path('canjear/<int:recompensa_id>/', views.canjear_recompensa, name='canjear_recompensa'),
    path('nueva-entrega/', views.nueva_entrega, name='nueva_entrega'),
    path('historial/', views.historial, name='historial'),
    
    # Página de prueba
    path('index/', views.index, name='index'),
]