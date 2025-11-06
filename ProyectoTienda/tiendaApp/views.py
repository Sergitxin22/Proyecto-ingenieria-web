from django.shortcuts import render
from .models import Cliente, Prenda, Pedido
from django.shortcuts import render, get_object_or_404

def index(request):
    return render(request,'index.html')
# Create your views here.

def lista_prendas(request):
    prendas = Prenda.objects.all()
    context = {'prendas': prendas}
    return render(request, 'prendas/lista_prendas.html', context)

def lista_pedidos(request):
    pedidos = Pedido.objects.all()
    context = {"pedidos": pedidos}
    return render(request, 'pedidos/lista_pedidos.html', context)

def lista_clientes(request):
    clientes = Cliente.objects.all()
    context = {"clientes": clientes}
    return render(request, 'clientes/lista_clientes.html', context)

def detalles_prenda(request, pk):
    prenda = get_object_or_404(Prenda, pk=pk)
    context = {'Prenda': prenda}
    return render(request, 'prendas/detalles_prenda.html', context)

def detalles_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    context = {'Pedido': pedido}
    return render(request, 'pedidos/detalles_pedido.html', context)

def detalles_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    context = {'Cliente': cliente}
    return render(request, 'clientes/detalles_cliente.html', context)