from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from .models import Cliente, Prenda, Pedido, Categoria, VariantePrenda, ItemPedido
from django.views.generic import ListView, DetailView
from .forms import AddToCartForm,LoginForm
from .carrito import Carrito
from decimal import Decimal

def base(request):
    return render(request,'pages/home.html')


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data["nombreUsuario"]
            password = form.cleaned_data["password"]

            # Si tus clientes NO son usuarios del sistema User:
            try:
                cliente = Cliente.objects.get(email=email, password=password)
                request.session["cliente_id"] = cliente.id
                messages.success(request, f"Bienvenido {cliente.nombre}")
                return redirect("lista_prendas")
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
        return context
    
    def post(self, request, *args, **kwargs):
        prenda = self.get_object()
        form = AddToCartForm(request.POST, prenda=prenda)

        if form.is_valid():
            variante = form.cleaned_data["variante"]
            cantidad = form.cleaned_data["cantidad"]

            # Agregar al carrito
            carrito = Carrito(request)
            carrito.agregar(variante=variante, cantidad=cantidad)

            messages.success(request, f'Se agregaron {cantidad} unidades de {variante} al carrito')
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
        carrito.agregar(variante=variante, cantidad=cantidad)
        
        messages.success(request, f'Se agregó {cantidad}x {variante} al carrito')
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
        carrito.actualizar_cantidad(variante, cantidad)
        
        messages.success(request, 'Carrito actualizado')
        return redirect('ver_carrito')

class CheckoutView(View):
    """Vista para procesar el pago y crear el pedido"""
    def get(self, request):
        carrito = Carrito(request)
        if len(carrito) == 0:
            messages.warning(request, 'Tu carrito está vacío')
            return redirect('lista_prendas')
        
        return render(request, 'carrito/checkout.html', {'carrito': carrito})
    
    def post(self, request):
        carrito = Carrito(request)
        
        if len(carrito) == 0:
            messages.error(request, 'No puedes realizar un pedido con un carrito vacío')
            return redirect('lista_prendas')
        
        # Obtener o crear cliente (simplificado - aquí deberías tener autenticación)
        cliente_id = request.POST.get('cliente_id')
        if cliente_id:
            cliente = get_object_or_404(Cliente, id=cliente_id)
        else:
            # Por ahora permitimos pedidos sin cliente (modo invitado)
            cliente = None
        
        # Crear el pedido
        pedido = Pedido.objects.create(
            cliente=cliente,
            estado='pendiente',
            precio_total=0
        )
        
        # Crear los items del pedido
        for item in carrito:
            ItemPedido.objects.create(
                pedido=pedido,
                variante=item['variante'],
                cantidad=item['cantidad'],
                precio_unitario=Decimal(item['precio'])
            )
        
        # Calcular el total del pedido
        pedido.calcular_total()
        
        # Limpiar el carrito
        carrito.limpiar()
        
        messages.success(request, f'¡Pedido #{pedido.id} realizado con éxito!')
        return redirect('detalles_pedido', pk=pedido.id)
