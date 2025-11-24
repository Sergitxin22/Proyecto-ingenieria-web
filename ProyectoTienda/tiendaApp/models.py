from django.db import models

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    foto = models.URLField(max_length=200, blank=True, null=True)
    #siempre que añada nuevos campos y ya tengo info en BD, ponemos blank true y null true

    class Meta: #Para visualizat el nombre en singular y plural del modelo en ADMIN
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nombre

class Prenda(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    talla = models.CharField(max_length=100)
    precio = models.CharField(max_length=100)
    foto = models.URLField(max_length=200, blank=True, null=True)

    class Meta: #Para visualizat el nombre en singular y plural del modelo en ADMIN
        verbose_name = "Prenda"
        verbose_name_plural = "Prendas"

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    precio = models.CharField(max_length=100, blank=True)
    fecha = models.DateField(max_length=100)
    cliente = models.ForeignKey(Cliente, on_delete= models.CASCADE, related_name='usuarioPedido')
    prendas = models.ManyToManyField(Prenda, related_name="prendasPedido")

    class Meta: #Para visualizat el nombre en singular y plural del modelo en ADMIN
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

class Categoria(models.Model):
    categoria = models.CharField(max_length=100)
    prendas = models.ManyToManyField(Prenda, related_name="prendasCategoria")

    class Meta: #Para visualizat el nombre en singular y plural del modelo en ADMIN
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"