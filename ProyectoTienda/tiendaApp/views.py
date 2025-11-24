from django.shortcuts import render
from .models import Cliente, Prenda, Pedido, Categoria
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

def index(request):
    return render(request,'index.html')

def base(request):
    return render(request,'base.html')
# # Create your views here.

# def lista_prendas(request):
#     prendas = Prenda.objects.all()
#     context = {'prendas': prendas}
#     return render(request, 'prendas/lista_prendas.html', context)

# def lista_pedidos(request):
#     pedidos = Pedido.objects.all()
#     context = {"pedidos": pedidos}
#     return render(request, 'pedidos/lista_pedidos.html', context)

# def lista_clientes(request):
#     clientes = Cliente.objects.all()
#     context = {"clientes": clientes}
#     return render(request, 'clientes/lista_clientes.html', context)

def header(request):
    categorias = Categoria.objects.all()
    context = {"categorias": categorias}
    return render(request, 'components/header.html', context)

# def detalles_prenda(request, pk):
#     prenda = get_object_or_404(Prenda, pk=pk)
#     context = {'Prenda': prenda}
#     return render(request, 'prendas/detalles_prenda.html', context)

# def detalles_pedido(request, pk):
#     pedido = get_object_or_404(Pedido, pk=pk)
#     context = {'Pedido': pedido}
#     return render(request, 'pedidos/detalles_pedido.html', context)

# def detalles_cliente(request, pk):
#     cliente = get_object_or_404(Cliente, pk=pk)
#     context = {'Cliente': cliente}
#     return render(request, 'clientes/detalles_cliente.html', context)

# def detalles_categoria(request, pk):
#     categoria = get_object_or_404(Categoria, pk=pk)
#     context = {'Categoria': categoria}
#     return render(request, 'categorias/detalles_categoria.html', context)

class PrendaListView(ListView):
    model = Prenda
    context_object_name = "prendas"
    template_name = "prendas/lista_prendas.html"

class PrendaDetailView(DetailView):
    model = Prenda
    context_object_name = "prendas"
    template_name = "prendas/detalle_prenda.html"
    
class PedidoListView(ListView):
    model = Pedido
    context_object_name = "pedidos"
    template_name = "pedidos/lista_pedidos.html"

class PedidoDetailView(DetailView):
    model = Pedido
    context_object_name = "pedidos"
    template_name = "pedidos/detalle_pedido.html"

class ClienteListView(ListView):
    model = Cliente
    context_object_name = "clientes"
    template_name = "clientes/lista_clientes.html"

class ClienteDetailView(DetailView):
    model = Cliente
    context_object_name = "clientes"
    template_name = "clientes/detalle_cliente.html"

class CategoriaListView(ListView):
    model = Categoria
    context_object_name = "categorias"
    template_name = "categorias/lista_categorias.html"

class CategoriaDetailView(DetailView):
    model = Categoria
    context_object_name = "categorias"
    template_name = "categorias/detalle_categoria.html"