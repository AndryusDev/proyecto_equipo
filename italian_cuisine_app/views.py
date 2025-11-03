from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Pedido
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# Create your views here.
class VistaLogin(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('panel_principal')

    def get_success_url(self):
        return self.success_url

def lista_pedidos(request):
    # El modelo Pedido puede definir `fecha` o `hora_creacion` como campo DateTimeField.
    # Elegimos el que exista para ordenar.
    if any(field.name == 'hora_creacion' for field in Pedido._meta.fields):
        pedidos = Pedido.objects.all().order_by('-hora_creacion')
    else:
        pedidos = Pedido.objects.all().order_by('-fecha')

    return render(request, 'pedidos/lista_pedidos.html', {'pedidos': pedidos})