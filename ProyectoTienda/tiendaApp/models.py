from django.db import models

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    foto = models.URLField(max_length=200, blank=True, null=True)
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
    descripcion = models.CharField(max_length=100)
    talla = models.CharField(max_length=100)
    precio = models.CharField(max_length=100)
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
    precio = models.CharField(max_length=100, blank=True)
    fecha = models.DateField(auto_now_add=True, null=True)
    cliente = models.ForeignKey(Cliente, on_delete= models.CASCADE, related_name='usuarioPedido')
    prendas = models.ManyToManyField(Prenda, related_name="prendasPedido")

    class Meta: #Para visualizar el nombre en singular y plural del modelo en ADMIN
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

class FotoPrenda(models.Model):
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name="fotos")
    url = models.URLField(max_length=300)

    def __str__(self):
        return f"Foto de {self.prenda.nombre}"