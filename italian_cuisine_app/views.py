from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Pedido, Categoria, Plato, Empleado,DetallePedido, Mesa
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction



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
    

@method_decorator(login_required, name='dispatch')
class EliminarCategoriaView(View):
    def post(self, request, pk):
        categoria = get_object_or_404(Categoria, pk=pk)
        if categoria.platos.exists():
            messages.error(request, f"❌ No se puede eliminar la categoría '{categoria.nombre}' porque tiene platos asociados.")
            return redirect('platos_categorias')
        
        categoria.delete()
        messages.success(request, f"🗑️ Categoría '{categoria.nombre}' eliminada correctamente.")
        return redirect('platos_categorias')


@method_decorator(login_required, name='dispatch')
class EliminarPlatoView(View):
    def post(self, request, pk):
        plato = get_object_or_404(Plato, pk=pk)
        plato.delete()
        messages.success(request, f"🗑️ Plato '{plato.nombre}' eliminado correctamente.")
        return redirect('platos_categorias')
    

# =============================
# PANEL DE PEDIDOS (crear pedido)
# =============================
class PedidosView(LoginRequiredMixin, View):
    """Muestra el panel de creación de pedidos."""
    def get(self, request):
        categorias = Categoria.objects.prefetch_related('platos').all()
        mesas = Mesa.objects.all().order_by('numero')
        try:
            empleado = Empleado.objects.get(user=request.user)
        except Empleado.DoesNotExist:
            empleado = None
        return render(request, 'panel/pedidos.html', {
            'categorias': categorias,
            'mesas': mesas,
            'empleado': empleado
        })


class CrearPedidoView(LoginRequiredMixin, View):
    """Crea un nuevo pedido mediante POST."""
    def post(self, request):
        mesa_id = request.POST.get('mesa')
        platos = request.POST.getlist('platos')
        cantidades = request.POST.getlist('cantidades')

        if not mesa_id or not platos:
            messages.error(request, "Debe seleccionar una mesa y al menos un plato.")
            return redirect('pedidos')

        mesa = get_object_or_404(Mesa, id=mesa_id)

        # Validar si la mesa está ocupada
        if mesa.ocupada:
            messages.warning(request, f"La Mesa {mesa.numero} ya está ocupada.")
            return redirect('pedidos')

        with transaction.atomic():
            pedido = Pedido.objects.create(
                mesa=mesa,
                mesero=request.user,
                estado='espera',
                total=0
            )

            total = 0
            for i, plato_id in enumerate(platos):
                plato = get_object_or_404(Plato, id=plato_id)
                cantidad = int(cantidades[i])
                subtotal = plato.precio * cantidad
                DetallePedido.objects.create(
                    pedido=pedido,
                    plato=plato,
                    cantidad=cantidad,
                    subtotal=subtotal
                )
                total += subtotal

            pedido.total = total
            pedido.save()
            mesa.ocupada = True
            mesa.save()

        messages.success(request, f"Pedido #{pedido.id} creado correctamente.")
        return redirect('mis_pedidos')


class MisPedidosView(LoginRequiredMixin, View):
    """Muestra los pedidos del mesero logueado."""
    def get(self, request):
        pedidos = Pedido.objects.filter(mesero=request.user).select_related('mesa').prefetch_related('detallepedido_set__plato')
        try:
            empleado = Empleado.objects.get(user=request.user)
        except Empleado.DoesNotExist:
            empleado = None
        return render(request, 'mis_pedidos.html', {'pedidos': pedidos, 'empleado': empleado})