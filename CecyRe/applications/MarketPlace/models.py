from django.db import models
from django.contrib.auth.hashers import make_password


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, null=False)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']  

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    ROLES = [
        ('comprador', 'Comprador'),
        ('vendedor', 'Vendedor'),
        ('admin', 'Administrador'),
    ]

    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=50, blank=True, null=True)
    apellido_materno = models.CharField(max_length=50, blank=True, null=True)
    rol = models.CharField(max_length=10, choices=ROLES, null=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    password = models.CharField(max_length=50, null=False)
    correo=models.EmailField(max_length=80)

    def save(self, *args, **kwargs):
        # Evita volver a cifrar contraseñas ya cifradas
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']  # Más recientes primero
        indexes = [
            models.Index(fields=['rol']),
            models.Index(fields=['fecha_registro']),
        ]
    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"

class Producto(models.Model):
    PUREZA = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    ESTADO = [
        ('disponible', 'Disponible'),
        ('no_disponible', 'No disponible'),
    ]

    id_producto = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    precio_kg = models.DecimalField(max_digits=10, decimal_places=2)
    peso_disponible_kg = models.DecimalField(max_digits=10, decimal_places=2)
    pureza = models.CharField(max_length=5, choices=PUREZA)
    estado = models.CharField(max_length=15, choices=ESTADO)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_publicacion']  # Más recientes primero
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['pureza']),
            models.Index(fields=['precio_kg']),
            models.Index(fields=['id_categoria']),
            models.Index(fields=['fecha_publicacion']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(precio_kg__gte=0),
                name='precio_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(peso_disponible_kg__gte=0),
                name='peso_positivo'
            ),
        ]

    def __str__(self):
        return self.nombre

class ImagenProducto(models.Model):
    id_imagen = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to="productos/")
    orden = models.IntegerField()

    class Meta:
        verbose_name = 'Imagen de producto'
        verbose_name_plural = 'Imágenes de productos'
        ordering = ['id_producto', 'orden']
        unique_together = ['id_producto', 'orden']

    def __str__(self):
        return f"Imagen {self.id_imagen} de {self.id_producto}"

class Carrito(models.Model):
    id_carrito = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        ordering = ['-fecha_creacion']  # Más recientes primero
        indexes = [
            models.Index(fields=['id_usuario']),
            models.Index(fields=['fecha_creacion']),
        ]

    def __str__(self):
        return f"Carrito {self.id_carrito} de {self.id_usuario}"

class ItemCarrito(models.Model):
    id_item = models.AutoField(primary_key=True)
    id_carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_kg = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item de carrito'
        verbose_name_plural = 'Items de carrito'
        ordering = ['id_carrito', 'id_item']
        indexes = [
            models.Index(fields=['id_carrito']),
            models.Index(fields=['id_producto']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(cantidad_kg__gt=0),
                name='cantidad_positiva'
            ),
            models.CheckConstraint(
                check=models.Q(precio_unitario__gte=0),
                name='precio_unitario_positivo'
            ),
        ]

    def __str__(self):
        return f"Item {self.id_item} ({self.id_producto})"

class OrdenVenta(models.Model):
    ESTADO_ORDEN = [
        ('completada', 'Completada'),
        ('pendiente', 'Pendiente'),
    ]

    id_orden = models.AutoField(primary_key=True)
    id_usuario_vendedor = models.ForeignKey(
        Usuario, 
        related_name='ventas_realizadas',
        on_delete=models.CASCADE
    )
    id_usuario_comprador = models.ForeignKey(
        Usuario, 
        related_name='compras_realizadas',
        on_delete=models.CASCADE
    )
    fecha = models.DateTimeField(auto_now_add=True)
    estado_orden = models.CharField(
        max_length=15, 
        choices=ESTADO_ORDEN, 
        default='pendiente'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Orden de venta'
        verbose_name_plural = 'Órdenes de venta'
        ordering = ['-fecha']  # Más recientes primero
        indexes = [
            models.Index(fields=['id_usuario_vendedor']),
            models.Index(fields=['id_usuario_comprador']),
            models.Index(fields=['estado_orden']),
            models.Index(fields=['fecha']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total__gte=0),
                name='total_positivo'
            ),
        ]

    def __str__(self):
        return f"Orden {self.id_orden}"

class DetalleOrden(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_orden = models.ForeignKey(OrdenVenta, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_kg = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de orden'
        verbose_name_plural = 'Detalles de orden'
        ordering = ['id_orden', 'id_detalle']
        indexes = [
            models.Index(fields=['id_orden']),
            models.Index(fields=['id_producto']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(cantidad_kg__gt=0),
                name='detalle_cantidad_positiva'
            ),
            models.CheckConstraint(
                check=models.Q(precio_unitario__gte=0),
                name='detalle_precio_positivo'
            ),
        ]

    def __str__(self):
        return f"Detalle {self.id_detalle} de orden {self.id_orden}"

class Pago(models.Model):
    METODOS = [
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('efectivo', 'Efectivo'),
        ('otro', 'Otro'),
    ]

    ESTADO_PAGO = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
    ]

    id_pago = models.AutoField(primary_key=True)
    id_orden = models.ForeignKey(OrdenVenta, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=15, choices=METODOS)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    estado_pago = models.CharField(max_length=15, choices=ESTADO_PAGO)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha']  # Más recientes primero
        indexes = [
            models.Index(fields=['id_orden']),
            models.Index(fields=['estado_pago']),
            models.Index(fields=['metodo_pago']),
            models.Index(fields=['fecha']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(monto__gt=0),
                name='monto_positivo'
            ),
        ]

    def __str__(self):
        return f"Pago {self.id_pago} - {self.metodo_pago}"

class Conversacion(models.Model):
    id_conversacion = models.AutoField(primary_key=True)
    id_usuario1 = models.ForeignKey(
        Usuario, 
        related_name='conversaciones_enviadas', 
        on_delete=models.CASCADE
    )
    id_usuario2 = models.ForeignKey(
        Usuario, 
        related_name='conversaciones_recibidas', 
        on_delete=models.CASCADE
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
        ordering = ['-fecha_creacion']  # Más recientes primero
        indexes = [
            models.Index(fields=['id_usuario1']),
            models.Index(fields=['id_usuario2']),
            models.Index(fields=['fecha_creacion']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['id_usuario1', 'id_usuario2'],
                name='conversacion_unica'
            ),
        ]

    def __str__(self):
        return f"Conversación entre {self.id_usuario1} y {self.id_usuario2}"

class Mensaje(models.Model):
    id_mensaje = models.AutoField(primary_key=True)
    id_conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['fecha_hora']  # Orden cronológico
        indexes = [
            models.Index(fields=['id_conversacion']),
            models.Index(fields=['id_usuario']),
            models.Index(fields=['fecha_hora']),
            models.Index(fields=['leido']),
        ]

    def __str__(self):
        return f"Mensaje {self.id_mensaje} de {self.id_usuario}"