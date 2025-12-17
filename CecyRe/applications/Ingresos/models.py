from django.db import models
from applications.MarketPlace.models import Usuario, Producto,DetalleOrden


# -------------------------
#   CATEGORIA GASTO
# -------------------------
class CategoriaGasto(models.Model):
    id_categoria_gasto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'categoria_gastos'

    def __str__(self):
        return self.nombre


# -------------------------
#       GASTOS
# -------------------------
class Gastos(models.Model):
    id_gastos = models.AutoField(primary_key=True)
    concepto = models.CharField(max_length=50)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.TextField()
    factura_adjunto = models.CharField(max_length=150)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_categoria_gasto = models.ForeignKey(CategoriaGasto, on_delete=models.CASCADE)

    class Meta:
        db_table = 'gastos'


# -------------------------
#       VENTA EXTERNA
# -------------------------
class VentaExterna(models.Model):
    id_venta_externa = models.AutoField(primary_key=True)
    descripcion = models.TextField()
    cliente_nombre = models.CharField(max_length=50)
    cliente_contacto = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = 'venta_externa'


# -------------------------
#   DETALLE VENTA EXTERNA
# -------------------------
class DetalleVentaExterna(models.Model):
    MATERIA_CHOICES = (
        ('1', 'Plástico'),
        ('2', 'Metal'),
        ('3', 'Papel'),
        ('4', 'Otro'),
    )

    id_detalle_venta_ex = models.AutoField(primary_key=True)
    materia = models.CharField(max_length=1, choices=MATERIA_CHOICES)
    cantidad_kg = models.DecimalField(max_digits=10, decimal_places=2)
    precio_kg = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    id_venta_externa = models.ForeignKey(VentaExterna, on_delete=models.CASCADE)

    class Meta:
        db_table = 'detalle_venta_externa'


# -------------------------
#         ORDEN VENTA
# -------------------------
class OrdenVenta(models.Model):
    ESTADO_CHOICES = (
        ('pagado', 'Pagado'),
        ('pendiente', 'Pendiente'),
    )

    id_orden = models.AutoField(primary_key=True)
    estado_orden = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = 'orden_venta'





# -------------------------
#            PAGO
# -------------------------
class Pago(models.Model):
    TIPO_CHOICES = (
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
    )

    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
    )

    id_pago = models.AutoField(primary_key=True)
    metodo_pago = models.CharField(max_length=50, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    estado_pago = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    id_orden = models.ForeignKey(OrdenVenta, on_delete=models.CASCADE)

    class Meta:
        db_table = 'pago'
