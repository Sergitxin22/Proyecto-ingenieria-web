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
