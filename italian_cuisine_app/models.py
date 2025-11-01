from django.db import models
from django.contrib.auth.models import User


# ==============================
#  EMPLEADO (datos del usuario)
# ==============================
class Empleado(models.Model):
    CARGOS = (
        ('administrador', 'Administrador'),
        ('mesero', 'Mesero'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=20, choices=CARGOS)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_ingreso = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.cargo})"


# ==============================
#  CATEGORÍA DE PLATOS
# ==============================
class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


# ==============================
#  PLATOS DEL MENÚ
# ==============================
class Plato(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    disponible = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='platos')
    imagen = models.ImageField(upload_to='platos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


# ==============================
#  MESAS
# ==============================
class Mesa(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    ocupada = models.BooleanField(default=False)

    def __str__(self):
        return f"Mesa {self.numero}"


# ==============================
#  PEDIDOS
# ==============================
class Pedido(models.Model):
    ESTADOS = (
        ('espera', 'En espera'),
        ('proceso', 'En proceso'),
        ('listo', 'Listo'),
    )

    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True)
    mesero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='espera')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Pedido #{self.id} - {self.estado}"

    def calcular_total(self):
        total = sum(detalle.subtotal for detalle in self.detallepedido_set.all())
        self.total = total
        self.save()


# ==============================
#  DETALLE DE PEDIDOS
# ==============================
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Calcula el subtotal antes de guardar
        self.subtotal = self.plato.precio * self.cantidad
        super().save(*args, **kwargs)
        # Actualiza el total del pedido automáticamente
        self.pedido.calcular_total()

    def __str__(self):
        return f"{self.plato.nombre} x {self.cantidad}"

# Nota: la clase Pedido ya estaba definida arriba con campos completos y relación con Mesa,
# User y DetallePedido. Nos aseguramos de que ese modelo es el único en este archivo.