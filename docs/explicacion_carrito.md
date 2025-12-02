# Explicación del Carrito de Compras

Este documento detalla la implementación técnica del carrito de compras en `ProyectoTienda`, el cual persiste los datos utilizando las sesiones de Django.

## 1. Estructura de Datos
El carrito no se guarda en la base de datos hasta que se confirma el pedido. Mientras tanto, vive en la sesión del usuario (`request.session`).

La estructura interna del diccionario del carrito es:
```python
{
    'variante_id_1': {
        'cantidad': 2,
        'precio': '15000.00'  # Guardado como string para serialización JSON
    },
    'variante_id_2': {
        'cantidad': 1,
        'precio': '25000.00'
    }
}
```

## 2. Clase `Carrito` (`carrito.py`)
Esta clase es el núcleo de la lógica del carrito. Actúa como una interfaz para manipular la sesión.

### Inicialización (`__init__`)
- Recupera el diccionario `carrito` de `request.session`.
- Si no existe, crea uno vacío `{}` y lo asigna a la sesión.

### Métodos Principales
- **`agregar(variante, cantidad)`**:
    - Recibe un objeto `VariantePrenda`.
    - Usa el ID de la variante como clave.
    - Si el producto ya está, suma la cantidad. Si no, lo crea.
    - Llama a `guardar()`.
- **`guardar()`**:
    - Ejecuta `self.session.modified = True`. Esto es crucial para decirle a Django que el objeto sesión ha cambiado y debe guardarse en la base de datos de sesiones.
- **`eliminar(variante)`**:
    - Elimina la clave correspondiente al ID de la variante del diccionario.
- **`actualizar_cantidad(variante, cantidad)`**:
    - Permite fijar una cantidad específica (usado en la vista de editar carrito).
- **`limpiar()`**:
    - Elimina la clave `carrito` de la sesión completamente (usado al finalizar compra).
- **`get_total_precio()`**:
    - Itera sobre los items y suma `precio * cantidad`. Convierte los precios de string a `Decimal` para cálculos precisos.

### Iteración (`__iter__`)
Este es un método mágico que permite hacer `for item in carrito` en las vistas y templates.
1. Obtiene todos los IDs de variantes del carrito.
2. Hace una consulta a la base de datos (`VariantePrenda.objects.filter(...)`) para traer los objetos reales con toda su información (nombre, foto, talla, etc.).
3. Combina la información de la sesión (cantidad, precio guardado) con la información de la base de datos (objeto variante).
4. Calcula el subtotal por item (`precio * cantidad`).
5. Devuelve un generador con los items enriquecidos.

## 3. Integración en Vistas (`views.py`)

### Gestión del Carrito
Se utilizan vistas basadas en clases (`View`) para acciones específicas:
- **`CarritoView` (GET)**: Instancia `Carrito(request)` y lo pasa al template `carrito.html`.
- **`AgregarAlCarritoView` (POST)**: Recibe `variante_id` y `cantidad`. Llama a `carrito.agregar()`.
- **`EliminarDelCarritoView` (POST)**: Llama a `carrito.eliminar()`.
- **`ActualizarCarritoView` (POST)**: Llama a `carrito.actualizar_cantidad()`.

### Checkout (`CheckoutView`)
Es el proceso final donde el carrito se convierte en un `Pedido`.
1. **Validación**: Verifica que el usuario esté logueado (token) y que el carrito no esté vacío.
2. **Creación de Pedido**: Crea un objeto `Pedido` con estado 'pendiente'.
3. **Creación de Items**: Itera sobre el carrito y crea objetos `ItemPedido` en la base de datos, vinculándolos al pedido.
4. **Cálculo de Total**: Llama a `pedido.calcular_total()` para guardar el monto final.
5. **Limpieza**: Llama a `carrito.limpiar()` para vaciar la sesión.

## 4. Context Processor (`context_processor.py`)
Para mostrar el contador de items en el header (ej: "Carrito (3)"), se usa `carrito_processor`:
```python
def carrito_processor(request):
    carrito = Carrito(request)
    return {
        'carrito_total_items': len(carrito),
        'carrito_precio_total': carrito.get_total_precio()
    }
```
Esto evita tener que instanciar el carrito en cada vista manualmente solo para mostrar el contador.

## 5. Frontend
- **`carrito.html`**: Itera sobre el carrito usando el método `__iter__` de la clase python, mostrando foto, nombre, precio y controles para subir/bajar cantidad.
- **`header.html`**: Usa la variable `carrito_total_items` inyectada por el context processor.
