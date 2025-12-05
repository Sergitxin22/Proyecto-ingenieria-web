from decimal import Decimal
from .models import VariantePrenda, Prenda

class Carrito:
    def __init__(self, request):
        """
        Inicializa el carrito
        """
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            # Guardar un carrito vacío en la sesión
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def agregar(self, variante, cantidad=1):
        """
        Agrega una variante de prenda al carrito o actualiza su cantidad
        """
        variante_id = str(variante.id)
        
        # Verificar stock disponible
        cantidad_actual = self.carrito.get(variante_id, {}).get('cantidad', 0)
        cantidad_total = cantidad_actual + cantidad
        
        if cantidad_total > variante.stock:
            raise ValueError(f'Stock insuficiente. Solo hay {variante.stock} unidades disponibles.')
        
        if variante_id not in self.carrito:
            self.carrito[variante_id] = {
                'cantidad': 0,
                'precio': str(variante.prenda.precio)
            }
        
        self.carrito[variante_id]['cantidad'] += cantidad
        self.guardar()

    def guardar(self):
        """
        Marca la sesión como modificada para asegurarse de que se guarde
        """
        self.session.modified = True

    def eliminar(self, variante):
        """
        Elimina una variante del carrito
        """
        variante_id = str(variante.id)
        if variante_id in self.carrito:
            del self.carrito[variante_id]
            self.guardar()

    def actualizar_cantidad(self, variante, cantidad):
        """
        Actualiza la cantidad de una variante en el carrito
        """
        variante_id = str(variante.id)
        if variante_id in self.carrito:
            if cantidad > 0:
                # Verificar stock disponible
                if cantidad > variante.stock:
                    raise ValueError(f'Stock insuficiente. Solo hay {variante.stock} unidades disponibles.')
                self.carrito[variante_id]['cantidad'] = cantidad
            else:
                del self.carrito[variante_id]
            self.guardar()

    def limpiar(self):
        """
        Elimina el carrito de la sesión
        """
        del self.session['carrito']
        self.guardar()

    def __iter__(self):
        """
        Itera sobre los items en el carrito y obtiene las variantes de la base de datos
        """
        variantes_ids = self.carrito.keys()
        variantes = VariantePrenda.objects.filter(id__in=variantes_ids).select_related('prenda')
        carrito = self.carrito.copy()

        for variante in variantes:
            carrito[str(variante.id)]['variante'] = variante

        for item in carrito.values():
            item['precio'] = Decimal(item['precio'])
            item['total'] = item['precio'] * item['cantidad']
            yield item

    def __len__(self):
        """
        Cuenta todos los items en el carrito
        """
        return sum(item['cantidad'] for item in self.carrito.values())

    def get_total_precio(self):
        """
        Calcula el precio total del carrito
        """
        return sum(Decimal(item['precio']) * item['cantidad'] for item in self.carrito.values())

    def get_items_count(self):
        """
        Obtiene el número de items únicos en el carrito
        """
        return len(self.carrito)
