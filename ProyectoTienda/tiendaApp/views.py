from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from .models import Cliente, Prenda, Pedido, Categoria, VariantePrenda, ItemPedido
from django.views.generic import ListView, DetailView
from .forms import AddToCartForm,LoginForm
from .carrito import Carrito
from decimal import Decimal
from .auth_utils import crear_sesion_usuario, obtener_cliente_por_token, cerrar_sesion
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def base(request):
    return render(request,'pages/home.html')

def test_500(request):
    """Vista para probar el error 500"""
    raise Exception("Error 500 de prueba")


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data["nombreUsuario"]
            password = form.cleaned_data["password"]

            # Si tus clientes NO son usuarios del sistema User:
            try:
                cliente = Cliente.objects.get(email=email, password=password)
                
                # Generar token y crear sesión
                token = crear_sesion_usuario(cliente)
                
                # Guardar el token en la sesión de Django
                request.session["auth_token"] = token
                request.session["cliente_id"] = cliente.id
                
                messages.success(request, f"Bienvenido {cliente.nombre}")
                return redirect("home")
            except Cliente.DoesNotExist:
                messages.error(request, "Email o contraseña incorrectos.")

    return render(request, "pages/login.html", {"form": form})

def signup_view(request):
    from .forms import RegistroForm

    form = RegistroForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            Cliente.objects.create(
              nombre=form.cleaned_data["nombre"],
              apellido=form.cleaned_data["apellido"],
              email=form.cleaned_data["email"],
              password=form.cleaned_data["password"],  # Uso simple, sin hashing
            )

            messages.success(request, "Cuenta creada correctamente.")
            return redirect("login")

    return render(request, "pages/signUp.html", {"form": form})


def logout_view(request):
    """Cierra la sesión del usuario y desactiva su token"""
    token = request.session.get('auth_token')
    if token:
        cerrar_sesion(token)
    
    messages.success(request, "Sesión cerrada correctamente")
    return redirect('home')
    


class PrendaListView(ListView):
    model = Prenda
    context_object_name = "prendas"
    template_name = "prendas/lista_prendas.html"

class PrendaDetailView(DetailView):
    model = Prenda
    context_object_name = "prenda"
    template_name = "prendas/detalles_prenda.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prenda = self.get_object()
        context["form"] = AddToCartForm(prenda=prenda)
        # Pasar datos de stock de cada variante para JavaScript
        context["variantes_stock"] = {v.id: v.stock for v in prenda.variantes.all()}
        return context
    
    def post(self, request, *args, **kwargs):
        prenda = self.get_object()
        form = AddToCartForm(request.POST, prenda=prenda)

        if form.is_valid():
            variante = form.cleaned_data["variante"]
            cantidad = form.cleaned_data["cantidad"]

            # Agregar al carrito
            carrito = Carrito(request)
            try:
                carrito.agregar(variante=variante, cantidad=cantidad)
                messages.success(request, f'Se agregaron {cantidad} unidades de {variante} al carrito')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Error al agregar al carrito. Por favor, verifica los datos.')
        
        return redirect('detalles_prenda', pk=prenda.pk)

    
class PedidoListView(ListView):
    model = Pedido
    context_object_name = "pedidos"
    template_name = "pedidos/lista_pedidos.html"

class PedidoDetailView(DetailView):
    model = Pedido
    context_object_name = "pedido"
    template_name = "pedidos/detalles_pedido.html"

class ClienteListView(ListView):
    model = Cliente
    context_object_name = "clientes"
    template_name = "clientes/lista_clientes.html"

class ClienteDetailView(DetailView):
    model = Cliente
    context_object_name = "cliente"
    template_name = "clientes/detalles_cliente.html"

class CategoriaListView(ListView):
    model = Categoria
    context_object_name = "categorias"
    template_name = "categorias/lista_categorias.html"

class CategoriaDetailView(DetailView):
    model = Categoria
    context_object_name = "categoria"
    template_name = "categorias/detalles_categoria.html"

# Vistas del Carrito
class CarritoView(View):
    """Vista para mostrar el carrito de compras"""
    def get(self, request):
        carrito = Carrito(request)
        return render(request, 'carrito/carrito.html', {'carrito': carrito})

class AgregarAlCarritoView(View):
    """Vista para agregar items al carrito"""
    def post(self, request, variante_id):
        variante = get_object_or_404(VariantePrenda, id=variante_id)
        cantidad = int(request.POST.get('cantidad', 1))
        
        carrito = Carrito(request)
        try:
            carrito.agregar(variante=variante, cantidad=cantidad)
            messages.success(request, f'Se agregó {cantidad}x {variante} al carrito')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('ver_carrito')

class EliminarDelCarritoView(View):
    """Vista para eliminar un item del carrito"""
    def post(self, request, variante_id):
        variante = get_object_or_404(VariantePrenda, id=variante_id)
        carrito = Carrito(request)
        carrito.eliminar(variante)
        
        messages.success(request, f'Se eliminó {variante} del carrito')
        return redirect('ver_carrito')

class ActualizarCarritoView(View):
    """Vista para actualizar la cantidad de un item"""
    def post(self, request, variante_id):
        variante = get_object_or_404(VariantePrenda, id=variante_id)
        cantidad = int(request.POST.get('cantidad', 1))
        
        carrito = Carrito(request)
        try:
            carrito.actualizar_cantidad(variante, cantidad)
            messages.success(request, 'Carrito actualizado')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('ver_carrito')

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