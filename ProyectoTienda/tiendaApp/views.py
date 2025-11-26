from django.shortcuts import render
from .models import Cliente, Prenda, Pedido, Categoria
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

def base(request):
    return render(request,'pages/home.html')

class PrendaListView(ListView):
    model = Prenda
    context_object_name = "prendas"
    template_name = "prendas/lista_prendas.html"

class PrendaDetailView(DetailView):
    model = Prenda
    context_object_name = "prenda"
    template_name = "prendas/detalles_prenda.html"
    
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