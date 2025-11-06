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

def detalle_prenda(request, pk):
    Prenda = get_object_or_404(Prenda, pk=pk)
    context = {'Prenda': Prenda}
    return render(request, 'prendas/detalle_prenda.html', context)

def detalle_pedido(request, pk):
    Pedido = get_object_or_404(Pedido, pk=pk)
    context = {'Pedido': Pedido}
    return render(request, 'pedidos/detalle_pedido.html', context)

def detalle_cliente(request, pk):
    Cliente = get_object_or_404(Cliente, pk=pk)
    context = {'Cliente': Cliente}
    return render(request, 'clientes/detalle_cliente.html', context)


