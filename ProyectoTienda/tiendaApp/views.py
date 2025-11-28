from django.shortcuts import render
from django.http import JsonResponse
from .models import Cliente, Prenda, Pedido, Categoria
from django.views.generic import ListView, DetailView
from .forms import AddToCartForm

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prenda = self.get_object()
        context["form"] = AddToCartForm(prenda=prenda)
        return context
    
    def post(self, request, *args, **kwargs):
        prenda = self.get_object()
        form = AddToCartForm(request.POST, prenda=prenda)

        cleaned_payload = form.data.copy()
        cleaned_payload.pop("csrfmiddlewaretoken", None)

        if form.is_valid():
            variante = form.cleaned_data["variante"]
            cantidad = form.cleaned_data["cantidad"]

            # Aquí va la lógica real del carrito.
            print("Añadir al carrito:", variante, cantidad)

            return JsonResponse(
                {
                    "mensaje": "Formulario recibido",
                    "peticion": cleaned_payload,
                    "datos_normalizados": {
                        "variante_id": variante.pk,
                        "variante": str(variante),
                        "cantidad": cantidad,
                    },
                }
            )

        # Si el form NO es válido, recargar con errores
        return JsonResponse(
            {
                "mensaje": "Formulario inválido",
                "peticion": cleaned_payload,
                "errores": form.errors,
            },
            status=400,
        )
    
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