from django.db import models
from django.contrib.auth.models import User

class Rango(models.Model):
    nombre = models.CharField(max_length=50)
    puntos_minimos = models.IntegerField()
    puntos_maximos = models.IntegerField()
    imagen_insignia = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Rango'
        verbose_name_plural = 'Rangos'
    
    def __str__(self):
        return self.nombre

class MaterialValor(models.Model):
    nombre = models.CharField(max_length=100)
    puntos_por_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Material Valor'
        verbose_name_plural = 'Materiales Valor'
    
    def __str__(self):
        return self.nombre

class Recolector(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)  # Cambiado a OneToOne
    codigo_qr = models.CharField(max_length=100, unique=True)
    puntos_acumulados = models.IntegerField(default=0)
    rango_actual = models.ForeignKey(Rango, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Recolector'
        verbose_name_plural = 'Recolectores'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.codigo_qr}"

class Entrega(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    recolector = models.ForeignKey(Recolector, on_delete=models.CASCADE)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entregas_encargado')
    fecha_hora_entrega = models.DateTimeField(auto_now_add=True)
    total_puntos_obtenidos = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='completado')
    
    class Meta:
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'

    def peso_total(self):
        """Calcula el peso total de la entrega"""
        return sum(detalle.peso_kg for detalle in self.detalles.all())
    
    def __str__(self):
        return f"Entrega {self.id} - {self.recolector}"
    
   

class DetalleEntrega(models.Model):
    entrega = models.ForeignKey(Entrega, on_delete=models.CASCADE, related_name='detalles')
    material = models.ForeignKey(MaterialValor, on_delete=models.CASCADE)
    peso_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    puntos_obtenidos = models.IntegerField(default=0)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Detalle de Entrega'
        verbose_name_plural = 'Detalles de Entrega'
    
    def save(self, *args, **kwargs):
        if self.material and self.peso_kg:
            self.puntos_obtenidos = int(float(self.peso_kg) * float(self.material.puntos_por_kg))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Detalle {self.id} - {self.material.nombre}"

class CategoriaRecompensa(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría de Recompensa'
        verbose_name_plural = 'Categorías de Recompensa'
    
    def __str__(self):
        return self.nombre

class Recompensa(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(CategoriaRecompensa, on_delete=models.SET_NULL, null=True, blank=True)
    costo_puntos = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Recompensa'
        verbose_name_plural = 'Recompensas'
    
    def __str__(self):
        return self.nombre

class Canje(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    recolector = models.ForeignKey(Recolector, on_delete=models.CASCADE)
    recompensa = models.ForeignKey(Recompensa, on_delete=models.CASCADE)
    fecha_canje = models.DateTimeField(auto_now_add=True)
    puntos_gastados = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    codigo_retiro = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Canje'
        
        verbose_name_plural = 'Canjes'
    
    def __str__(self):
        return f"Canje {self.id} - {self.recolector}"