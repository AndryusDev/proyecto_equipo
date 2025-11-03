from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Pedido
from django.urls import reverse_lazy
from .models import Empleado
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

# ---------- LOGIN ----------
class VistaLogin(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')  # ✅ Al iniciar sesión va al dashboard

def lista_pedidos(request):
    # El modelo Pedido puede definir `fecha` o `hora_creacion` como campo DateTimeField.
    # Elegimos el que exista para ordenar.
    if any(field.name == 'hora_creacion' for field in Pedido._meta.fields):
        pedidos = Pedido.objects.all().order_by('-hora_creacion')
    else:
        pedidos = Pedido.objects.all().order_by('-fecha')

    return render(request, 'pedidos/lista_pedidos.html', {'pedidos': pedidos})


# ---------- DASHBOARD PRINCIPAL ----------
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'panel/dashboard.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empleado = Empleado.objects.get(user=self.request.user)
        context["empleado"] = empleado
        context["cargo"] = empleado.cargo
        return context


# ---------- PANEL (REDIRECCIÓN AUTOMÁTICA) ----------
class PanelPrincipalView(LoginRequiredMixin, TemplateView):
    """Redirige automáticamente al dashboard cuando se entra a /panel/"""
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        return redirect('dashboard')  # ✅ redirige al dashboard automáticamente


# ---------- LOGOUT ----------
class VistaLogout(LogoutView):
    next_page = reverse_lazy('login')  # ✅ vuelve al login después de cerrar sesión # ✅ al cerrar sesión vuelve al login