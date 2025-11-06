from django.shortcuts import render
from django.http import HttpResponse
from .models import Cliente, Prenda, Pedido

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
