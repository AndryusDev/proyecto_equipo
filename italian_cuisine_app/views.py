from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Pedido, Categoria, Plato, Empleado
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView


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


#platos categorias

class PlatosCategoriasView(LoginRequiredMixin, TemplateView):
    template_name = "panel/platos_categorias.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empleado = Empleado.objects.get(user=self.request.user)
        categorias = Categoria.objects.all().order_by("nombre")
        platos = Plato.objects.select_related("categoria").all().order_by("nombre")

        context.update({
            "empleado": empleado,
            "categorias": categorias,
            "platos": platos
        })
        return context

    def post(self, request, *args, **kwargs):
        """ Maneja la creación de categorías y platos desde el mismo formulario """
        if "nombre_categoria" in request.POST:
            nombre = request.POST.get("nombre_categoria")
            if not Categoria.objects.filter(nombre__iexact=nombre).exists():
                Categoria.objects.create(nombre=nombre)
                messages.success(request, "✅ Categoría agregada exitosamente.")
            else:
                messages.warning(request, "⚠️ Esa categoría ya existe.")
            return redirect("platos_categorias")

        if "nombre_plato" in request.POST:
            nombre = request.POST.get("nombre_plato")
            descripcion = request.POST.get("descripcion")
            precio = request.POST.get("precio")
            disponible = bool(request.POST.get("disponible"))
            categoria_id = request.POST.get("categoria")
            imagen = request.FILES.get("imagen")

            if categoria_id:
                categoria = Categoria.objects.get(id=categoria_id)
                Plato.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=precio,
                    disponible=disponible,
                    categoria=categoria,
                    imagen=imagen
                )
                messages.success(request, "✅ Plato agregado correctamente.")
            else:
                messages.error(request, "❌ Debe seleccionar una categoría.")
            return redirect("platos_categorias")

        return redirect("platos_categorias")


class AgregarCategoriaView(LoginRequiredMixin, CreateView):
    model = Categoria
    fields = ["nombre"]
    success_url = reverse_lazy("platos_categorias")

    def form_valid(self, form):
        messages.success(self.request, "Categoría añadida correctamente.")
        return super().form_valid(form)


class AgregarPlatoView(LoginRequiredMixin, CreateView):
    model = Plato
    fields = ["nombre", "descripcion", "precio", "disponible", "categoria", "imagen"]
    success_url = reverse_lazy("platos_categorias")

    def form_valid(self, form):
        messages.success(self.request, "Plato añadido correctamente.")
        return super().form_valid(form)