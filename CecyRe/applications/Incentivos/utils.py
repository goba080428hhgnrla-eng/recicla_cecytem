import uuid
from django.db import transaction
from .models import Recolector, Rango

def generar_codigo_qr(username):
    """Genera un código QR único para el recolector"""
    return f"REC-{username.upper()}-{str(uuid.uuid4())[:8]}"

def actualizar_rango_recolector(recolector):
    """Actualiza el rango del recolector basado en sus puntos"""
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

def calcular_puntos(peso_kg, material):
    """Calcula los puntos obtenidos basados en peso y material"""
    return int(float(peso_kg) * float(material.puntos_por_kg))