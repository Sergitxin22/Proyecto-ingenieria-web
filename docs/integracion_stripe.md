# Guía de Integración de Stripe en tu Proyecto Django

## Paso 1: Instalar la librería de Stripe

```bash
pip install stripe
```

## Paso 2: Configurar las claves de Stripe

### 2.1 Obtener las claves de Stripe
1. Crea una cuenta en [Stripe](https://stripe.com)
2. Ve a **Developers** → **API keys**
3. Copia tu **Publishable key** y **Secret key** (usa las de prueba para desarrollo)

### 2.2 Agregar las claves a `settings.py`

En `ProyectoTienda/settings.py`, agrega al final del archivo:

```python
# Configuración de Stripe
STRIPE_PUBLIC_KEY = 'pk_test_tu_clave_publica_aqui'
STRIPE_SECRET_KEY = 'sk_test_tu_clave_secreta_aqui'
STRIPE_WEBHOOK_SECRET = 'whsec_tu_webhook_secret_aqui'  # Lo obtendrás después

# URL base para redirecciones de Stripe
SITE_URL = 'http://127.0.0.1:8000'  # Cambiar en producción
```

## Paso 3: Actualizar el modelo Pedido

### 3.1 Agregar campos de Stripe al modelo

En `tiendaApp/models.py`, actualiza la clase `Pedido`:

```python
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
    
    # Nuevos campos para Stripe
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    pagado = models.BooleanField(default=False)

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
```

### 3.2 Crear y aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

## Paso 4: Actualizar las vistas

### 4.1 Modificar `CheckoutView` en `tiendaApp/views.py`

Reemplaza la clase `CheckoutView` completa con:

```python
import stripe
from django.conf import settings

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutView(View):
    """Vista para mostrar el checkout"""
    def get(self, request):
        # Validar token antes de mostrar checkout
        cliente = obtener_cliente_por_token(request)
        if not cliente:
            messages.error(request, 'Debes iniciar sesión para realizar una compra')
            return redirect('signup')
        
        carrito = Carrito(request)
        if len(carrito) == 0:
            messages.warning(request, 'Tu carrito está vacío')
            return redirect('lista_prendas')
        
        context = {
            'carrito': carrito,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        }
        
        return render(request, 'carrito/checkout.html', context)

class CrearCheckoutSessionView(View):
    """Vista para crear la sesión de pago de Stripe"""
    def post(self, request):
        # Validar cliente autenticado
        cliente = obtener_cliente_por_token(request)
        if not cliente:
            messages.error(request, 'Sesión inválida. Por favor, inicia sesión')
            return redirect('login')
        
        carrito = Carrito(request)
        
        if len(carrito) == 0:
            messages.error(request, 'No puedes realizar un pedido con un carrito vacío')
            return redirect('lista_prendas')
        
        # Verificar stock disponible
        for item in carrito:
            variante = item['variante']
            cantidad = item['cantidad']
            if cantidad > variante.stock:
                messages.error(request, f'Stock insuficiente para {variante}. Solo hay {variante.stock} unidades disponibles.')
                return redirect('ver_carrito')
        
        # Crear el pedido temporal (sin reducir stock todavía)
        pedido = Pedido.objects.create(
            cliente=cliente,
            estado='pendiente',
            precio_total=0,
            pagado=False
        )
        
        # Crear los items del pedido
        line_items = []
        for item in carrito:
            variante = item['variante']
            cantidad = item['cantidad']
            
            ItemPedido.objects.create(
                pedido=pedido,
                variante=variante,
                cantidad=cantidad,
                precio_unitario=Decimal(item['precio'])
            )
            
            # Preparar items para Stripe
            line_items.append({
                'price_data': {
                    'currency': 'eur',  # Cambia según tu moneda
                    'product_data': {
                        'name': f"{variante.prenda.nombre} - {variante.descripcion}",
                    },
                    'unit_amount': int(float(item['precio']) * 100),  # Stripe usa centavos
                },
                'quantity': cantidad,
            })
        
        # Calcular el total del pedido
        pedido.calcular_total()
        
        try:
            # Crear sesión de Stripe Checkout
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=settings.SITE_URL + f'/carrito/pago-exitoso/?session_id={{CHECKOUT_SESSION_ID}}&pedido_id={pedido.id}',
                cancel_url=settings.SITE_URL + f'/carrito/pago-cancelado/?pedido_id={pedido.id}',
                metadata={
                    'pedido_id': pedido.id,
                    'cliente_id': cliente.id,
                }
            )
            
            # Guardar el ID de la sesión de Stripe
            pedido.stripe_checkout_session_id = checkout_session.id
            pedido.save()
            
            # Redirigir a Stripe Checkout
            return redirect(checkout_session.url, code=303)
            
        except Exception as e:
            # Si hay error, eliminar el pedido creado
            pedido.delete()
            messages.error(request, f'Error al procesar el pago: {str(e)}')
            return redirect('ver_carrito')

class PagoExitosoView(View):
    """Vista cuando el pago es exitoso"""
    def get(self, request):
        session_id = request.GET.get('session_id')
        pedido_id = request.GET.get('pedido_id')
        
        if not session_id or not pedido_id:
            messages.error(request, 'Información de pago incompleta')
            return redirect('home')
        
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Verificar la sesión de Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                # Marcar el pedido como pagado
                pedido.pagado = True
                pedido.estado = 'procesado'
                pedido.stripe_payment_intent_id = session.payment_intent
                pedido.save()
                
                # IMPORTANTE: Reducir el stock ahora que el pago fue exitoso
                for item in pedido.items.all():
                    variante = item.variante
                    variante.stock -= item.cantidad
                    variante.save()
                
                # Limpiar el carrito
                carrito = Carrito(request)
                carrito.limpiar()
                
                messages.success(request, f'¡Pago exitoso! Tu pedido #{pedido.id} ha sido confirmado.')
                return render(request, 'carrito/pago_exitoso.html', {'pedido': pedido})
            else:
                messages.warning(request, 'El pago aún está siendo procesado.')
                return redirect('home')
                
        except Pedido.DoesNotExist:
            messages.error(request, 'Pedido no encontrado')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Error al verificar el pago: {str(e)}')
            return redirect('home')

class PagoCanceladoView(View):
    """Vista cuando el pago es cancelado"""
    def get(self, request):
        pedido_id = request.GET.get('pedido_id')
        
        if pedido_id:
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                # Eliminar el pedido no pagado
                pedido.delete()
            except Pedido.DoesNotExist:
                pass
        
        messages.warning(request, 'Pago cancelado. Tu carrito sigue disponible.')
        return redirect('ver_carrito')

class StripeWebhookView(View):
    """Vista para manejar webhooks de Stripe"""
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        
        # Manejar el evento
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            pedido_id = session['metadata']['pedido_id']
            
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                pedido.pagado = True
                pedido.estado = 'procesado'
                pedido.stripe_payment_intent_id = session.get('payment_intent')
                pedido.save()
                
                # Reducir stock
                for item in pedido.items.all():
                    variante = item.variante
                    variante.stock -= item.cantidad
                    variante.save()
                    
            except Pedido.DoesNotExist:
                pass
        
        return JsonResponse({'status': 'success'})
```

### 4.2 Agregar imports necesarios al inicio de `views.py`

```python
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
```

## Paso 5: Actualizar URLs

En `tiendaApp/urls.py`, agrega las nuevas rutas:

```python
from django.urls import path
from .import views

urlpatterns=[
    path('', views.base, name='home'),
    path('prendas/', views.PrendaListView.as_view(), name='lista_prendas'),
    path('pedidos/', views.PedidoListView.as_view(), name='lista_pedidos'),
    path('clientes/', views.ClienteListView.as_view(), name='lista_clientes'),
    path('categorias/', views.CategoriaListView.as_view(), name='lista_categorias'),
    path('prendas/<int:pk>/', views.PrendaDetailView.as_view(), name='detalles_prenda'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='detalles_pedido'),
    path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='detalles_cliente'),
    path('categorias/<int:pk>/', views.CategoriaDetailView.as_view(), name='detalles_categoria'),
    path('login/',views.login_view,name='login'),
    path("registrarse/", views.signup_view, name="signup"),
    path('logout/', views.logout_view, name='logout'),
    
    # URLs del carrito
    path('carrito/', views.CarritoView.as_view(), name='ver_carrito'),
    path('carrito/agregar/<int:variante_id>/', views.AgregarAlCarritoView.as_view(), name='agregar_al_carrito'),
    path('carrito/eliminar/<int:variante_id>/', views.EliminarDelCarritoView.as_view(), name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:variante_id>/', views.ActualizarCarritoView.as_view(), name='actualizar_carrito'),
    path('carrito/checkout/', views.CheckoutView.as_view(), name='checkout'),
    
    # URLs de Stripe
    path('carrito/crear-checkout-session/', views.CrearCheckoutSessionView.as_view(), name='crear_checkout_session'),
    path('carrito/pago-exitoso/', views.PagoExitosoView.as_view(), name='pago_exitoso'),
    path('carrito/pago-cancelado/', views.PagoCanceladoView.as_view(), name='pago_cancelado'),
    path('stripe/webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
]
```

## Paso 6: Actualizar el template de Checkout

Reemplaza el contenido de `tiendaApp/templates/carrito/checkout.html`:

```html
{% extends 'base.html' %}

{% block content %}
<div class="container mt-5">
    <h1>Finalizar Compra</h1>

    {% if messages %}
    {% for message in messages %}
    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
    {% endfor %}
    {% endif %}

    <div class="row">
        <div class="col-md-8">
            <h3>Resumen del Pedido</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Variante</th>
                        <th>Cantidad</th>
                        <th>Precio</th>
                        <th>Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in carrito %}
                    <tr>
                        <td>{{ item.variante.prenda.nombre }}</td>
                        <td>{{ item.variante.descripcion }}</td>
                        <td>{{ item.cantidad }}</td>
                        <td>${{ item.precio }}</td>
                        <td>${{ item.total }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
                <tfoot>
                    <tr>
                        <th colspan="4" class="text-end">Total:</th>
                        <th>${{ carrito.get_total_precio }}</th>
                    </tr>
                </tfoot>
            </table>
        </div>

        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Datos del Cliente</h5>

                    {% if cliente %}
                    <div class="mb-4">
                        <div class="mb-3">
                            <label class="form-label fw-bold">Nombre:</label>
                            <p class="text-muted">{{ cliente.nombre }} {{ cliente.apellido }}</p>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Email:</label>
                            <p class="text-muted">{{ cliente.email }}</p>
                        </div>
                    </div>
                    {% endif %}

                    <form method="post" action="{% url 'crear_checkout_session' %}">
                        {% csrf_token %}

                        <div class="alert alert-info">
                            <small>
                                <i class="fas fa-info-circle"></i>
                                Serás redirigido a Stripe para realizar el pago de forma segura.
                            </small>
                        </div>

                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-success btn-lg">
                                <i class="fas fa-lock"></i> Pagar con Stripe
                            </button>
                            <a href="{% url 'ver_carrito' %}" class="btn btn-secondary">
                                Volver al carrito
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Paso 7: Crear templates de éxito y cancelación

### 7.1 Crear `tiendaApp/templates/carrito/pago_exitoso.html`

```html
{% extends 'base.html' %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card border-success">
                <div class="card-body text-center">
                    <div class="mb-4">
                        <i class="fas fa-check-circle text-success" style="font-size: 5rem;"></i>
                    </div>
                    <h1 class="card-title text-success">¡Pago Exitoso!</h1>
                    <p class="lead">Tu pedido ha sido procesado correctamente.</p>
                    
                    {% if pedido %}
                    <div class="alert alert-info mt-4">
                        <h5>Detalles del Pedido</h5>
                        <p><strong>Número de Pedido:</strong> #{{ pedido.id }}</p>
                        <p><strong>Total:</strong> ${{ pedido.precio_total }}</p>
                        <p><strong>Estado:</strong> {{ pedido.get_estado_display }}</p>
                    </div>
                    {% endif %}
                    
                    <div class="mt-4">
                        <a href="{% url 'home' %}" class="btn btn-primary me-2">
                            Volver al Inicio
                        </a>
                        <a href="{% url 'lista_prendas' %}" class="btn btn-outline-primary">
                            Seguir Comprando
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Paso 8: Configurar Webhooks de Stripe (Opcional pero Recomendado)

Los webhooks permiten que Stripe notifique a tu aplicación sobre eventos importantes.

### 8.1 Para desarrollo local con Stripe CLI

1. Instala [Stripe CLI](https://stripe.com/docs/stripe-cli)
2. Inicia sesión: `stripe login`
3. Escucha webhooks: `stripe listen --forward-to localhost:8000/stripe/webhook/`
4. Copia el webhook secret que te proporciona y agrégalo a `settings.py`

### 8.2 Para producción

1. Ve a **Developers** → **Webhooks** en tu dashboard de Stripe
2. Agrega un endpoint: `https://tudominio.com/stripe/webhook/`
3. Selecciona los eventos: `checkout.session.completed`
4. Copia el webhook secret y agrégalo a `settings.py`

## Paso 9: Pruebas

### Tarjetas de prueba de Stripe

Para probar los pagos, usa estas tarjetas:

- **Éxito:** `4242 4242 4242 4242`
- **Declinar:** `4000 0000 0000 0002`
- **Requiere autenticación:** `4000 0025 0000 3155`

**Datos adicionales para prueba:**
- Fecha de vencimiento: cualquier fecha futura
- CVC: cualquier 3 dígitos
- Código postal: cualquier código

## Paso 10: Ejecutar el proyecto

```bash
python manage.py runserver
```

Visita `http://127.0.0.1:8000/carrito/checkout/` para probar el checkout.

## Flujo de la Aplicación

1. Usuario agrega productos al carrito
2. Usuario hace clic en "Checkout"
3. Se muestra el resumen del pedido
4. Usuario hace clic en "Pagar con Stripe"
5. Se crea un pedido temporal en la base de datos
6. Usuario es redirigido a Stripe Checkout
7. Si el pago es exitoso:
   - Se marca el pedido como pagado
   - Se reduce el stock
   - Se limpia el carrito
   - Usuario ve página de éxito
8. Si el pago es cancelado:
   - Se elimina el pedido temporal
   - Usuario vuelve al carrito
   - Carrito mantiene los productos

## Ventajas de esta Implementación

✅ **Seguridad:** El pago se procesa completamente en Stripe  
✅ **Sin reducción prematura de stock:** El stock solo se reduce si el pago es exitoso  
✅ **Manejo de errores:** Si el pago falla, el usuario vuelve al carrito con un mensaje  
✅ **PCI Compliance:** No manejas datos sensibles de tarjetas  
✅ **Webhooks:** Confirmación redundante de pagos  

## Notas Importantes

- ⚠️ Usa las claves de prueba durante el desarrollo
- ⚠️ Nunca subas las claves secretas a repositorios públicos
- ⚠️ En producción, usa variables de entorno para las claves
- ⚠️ Cambia `SITE_URL` en producción a tu dominio real
- ⚠️ Ajusta la moneda según tu región (EUR, USD, etc.)
