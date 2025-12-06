from django.db import models

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    #siempre que añada nuevos campos y ya tengo info en BD, ponemos blank true y null true

    class Meta: #Para visualizar el nombre en singular y plural del modelo en ADMIN
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nombre
    
class Categoria(models.Model):
    categoria = models.CharField(max_length=100)
    
    class Meta: #Para visualizar el nombre en singular y plural del modelo en ADMIN
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.categoria

class Prenda(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categorias = models.ManyToManyField(Categoria, related_name="categoriasPrenda")

    class Meta:
        verbose_name = "Prenda"
        verbose_name_plural = "Prendas"

    def __str__(self):
        return self.nombre

class VariantePrenda(models.Model):
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name="variantes")
    descripcion = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Variante"
        verbose_name_plural = "Variantes"

    def __str__(self):
        return f"{self.prenda.nombre} - {self.descripcion}"

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('carrito', 'Carrito'),
        ('pendiente', 'Pendiente'),
        ('procesado', 'Procesado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateField(auto_now_add=True, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos', null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='carrito')

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido {self.id} - {self.estado}"

    def calcular_total(self):
        total = sum(item.subtotal() for item in self.items.all())
        self.precio_total = total
        self.save()
        return total

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    variante = models.ForeignKey(VariantePrenda, on_delete=models.CASCADE, related_name='items_pedido')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Items de Pedido"
        unique_together = ('pedido', 'variante')

    def __str__(self):
        return f"{self.cantidad}x {self.variante}"

    def subtotal(self):
        return self.cantidad * self.precio_unitario

class FotoPrenda(models.Model):
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name="fotos")
    url = models.URLField(max_length=300)

    def __str__(self):
        return f"Foto de {self.prenda.nombre}"
    
class Sesion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="sesion")
    token = models.CharField(max_length=256)
    activo= models.BooleanField(default=True)

    def __str__(self):
        return f"Token {self.token} de {self.cliente.nombre}"