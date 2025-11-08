from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView, TemplateView
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction

from .models import Empleado, Pedido, Categoria, Plato, DetallePedido, Mesa
from .forms import EmpleadoModelForm
from django.views.decorators.csrf import csrf_exempt


# ============================================================
# 🔹 Mixin para incluir el empleado logueado en el contexto
# ============================================================
class EmpleadoContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["empleado"] = Empleado.objects.filter(user=self.request.user).first()
        else:
            context["empleado"] = None
        return context


# ---------- LOGIN ----------
class VistaLogin(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')  # ✅ Al iniciar sesión va al dashboard


def lista_pedidos(request):
    if any(field.name == 'hora_creacion' for field in Pedido._meta.fields):
        pedidos = Pedido.objects.all().order_by('-hora_creacion')
    else:
        pedidos = Pedido.objects.all().order_by('-fecha')

    return render(request, 'pedidos/lista_pedidos.html', {'pedidos': pedidos})


# ---------- DASHBOARD PRINCIPAL ----------
class DashboardView(LoginRequiredMixin, EmpleadoContextMixin, TemplateView):
    template_name = 'panel/dashboard.html'
    login_url = '/login/'


# ---------- PANEL (REDIRECCIÓN AUTOMÁTICA) ----------
class PanelPrincipalView(LoginRequiredMixin, TemplateView):
    """Redirige automáticamente al dashboard cuando se entra a /panel/"""
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        return redirect('dashboard')


# ---------- LOGOUT ----------
class VistaLogout(LogoutView):
    next_page = reverse_lazy('login')


# ============================================================
# 🔹 GESTIÓN DE EMPLEADOS (con el mixin agregado)
# ============================================================
class UserListView(LoginRequiredMixin, EmpleadoContextMixin, ListView):
    model = Empleado
    template_name = 'empleados.html'
    context_object_name = 'empleados'
    paginate_by = 10
    login_url = 'login'


class EmpleadoDetailView(LoginRequiredMixin, EmpleadoContextMixin, DetailView):
    model = Empleado
    template_name = 'empleados_detail.html'
    context_object_name = 'empleado'
    login_url = 'login'
    partial_template_name = 'partials/empleado_detail_partial.html'

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return [self.partial_template_name]
        return [self.template_name]


class EmpleadoCreateView(LoginRequiredMixin, EmpleadoContextMixin, CreateView):
    model = Empleado
    form_class = EmpleadoModelForm
    template_name = 'empleados_form.html'
    partial_template_name = 'partials/empleado_form_partial.html'
    success_url = reverse_lazy('empleados')
    login_url = 'login'

    def form_valid(self, form):
        empleado = form.save()
        messages.success(self.request, f'Empleado creado correctamente (id: {empleado.pk}).')
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            row_html = render_to_string('partials/empleado_row_partial.html', {'empleado': empleado, 'request': self.request})
            return JsonResponse({'success': True, 'action': 'create', 'html': row_html, 'pk': empleado.pk})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.partial_template_name, {'form': form, 'request': self.request, 'submit_label': 'Crear'})
            return HttpResponse(html, status=400)
        return super().form_invalid(form)

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return [self.partial_template_name]
        return [self.template_name]


class EmpleadoUpdateView(LoginRequiredMixin, EmpleadoContextMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoModelForm
    template_name = 'empleados_form.html'
    partial_template_name = 'partials/empleado_form_partial.html'
    success_url = reverse_lazy('empleados')
    login_url = 'login'

    def form_valid(self, form):
        empleado = form.save()
        messages.success(self.request, f'Empleado {empleado.pk} actualizado correctamente.')
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            row_html = render_to_string('partials/empleado_row_partial.html', {'empleado': empleado, 'request': self.request})
            return JsonResponse({'success': True, 'action': 'update', 'html': row_html, 'pk': empleado.pk})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.partial_template_name, {'form': form, 'request': self.request, 'submit_label': 'Guardar'})
            return HttpResponse(html, status=400)
        return super().form_invalid(form)

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return [self.partial_template_name]
        return [self.template_name]


class EmpleadoDeleteView(LoginRequiredMixin, EmpleadoContextMixin, DeleteView):
    model = Empleado
    template_name = 'empleados_confirm_delete.html'
    success_url = reverse_lazy('empleados')
    login_url = 'login'
    partial_template_name = 'partials/empleado_confirm_delete_partial.html'

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return [self.partial_template_name]
        return [self.template_name]

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        pk = self.object.pk
        self.object.delete()
        messages.success(self.request, 'Empleado eliminado correctamente.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'action': 'delete', 'pk': pk})
        return redirect(success_url)


# ============================================================
# 🔹 PLATOS Y CATEGORÍAS
# ============================================================
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
    
@login_required
def obtener_plato(request, pk):
    """Retorna los datos de un plato en formato JSON."""
    plato = get_object_or_404(Plato, pk=pk)
    data = {
        'id': plato.id,
        'nombre': plato.nombre,
        'descripcion': plato.descripcion,
        'precio': float(plato.precio),
        'categoria': plato.categoria.id if plato.categoria else None,
        'disponible': plato.disponible,
    }
    return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class EditarPlatoView(LoginRequiredMixin, View):
    def post(self, request):
        plato_id = request.POST.get('plato_id')
        plato = get_object_or_404(Plato, id=plato_id)
        plato.nombre = request.POST.get('nombre')
        plato.descripcion = request.POST.get('descripcion')
        plato.precio = request.POST.get('precio')
        plato.disponible = 'disponible' in request.POST
        categoria_id = request.POST.get('categoria')
        if categoria_id:
            plato.categoria_id = categoria_id
        if 'imagen' in request.FILES:
            plato.imagen = request.FILES['imagen']
        plato.save()
        messages.success(request, f"✅ Plato '{plato.nombre}' actualizado correctamente.")
        return JsonResponse({'success': True})


# ============================================================
# 🔹 PANEL DE PEDIDOS
# ============================================================
class PedidosView(LoginRequiredMixin, View):
    """Vista principal para crear y gestionar pedidos."""
    
    def get(self, request):
        # Obtiene todas las categorías con sus platos (optimiza con prefetch)
        categorias = Categoria.objects.prefetch_related('platos').all()
        # Lista las mesas en orden numérico
        mesas = Mesa.objects.all().order_by('numero')
        # Obtiene el empleado asociado al usuario logueado (si existe)
        empleado = Empleado.objects.filter(user=request.user).first()

        contexto = {
            "categorias": categorias,
            "mesas": mesas,
            "empleado": empleado,
        }

        return render(request, "panel/pedidos.html", contexto)
    
def empleado_context(request):
    empleado = None
    if request.user.is_authenticated:
        empleado = Empleado.objects.filter(user=request.user).first()
    return {'empleado': empleado}


class CrearPedidoView(LoginRequiredMixin, View):
    """Guarda el pedido seleccionado desde la vista principal."""
    def post(self, request):
        mesa_id = request.POST.get('mesa')
        platos = request.POST.getlist('platos')
        cantidades = request.POST.getlist('cantidades')

        if not mesa_id or not platos:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Debe seleccionar una mesa y al menos un plato.'}, status=400)
            messages.error(request, "Debe seleccionar una mesa y al menos un plato.")
            return redirect('pedidos')

        mesa = get_object_or_404(Mesa, id=mesa_id)
        if mesa.ocupada:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': f'La Mesa {mesa.numero} ya está ocupada.'}, status=400)
            messages.warning(request, f"La Mesa {mesa.numero} ya está ocupada.")
            return redirect('pedidos')

        try:
            with transaction.atomic():
                pedido = Pedido.objects.create(
                    mesa=mesa,
                    mesero=request.user,
                    estado='en_proceso',
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

        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=500)
            messages.error(request, f"Error al crear pedido: {e}")
            return redirect('pedidos')

        # 👇 si viene de AJAX, responder con JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'id': pedido.id,
                'mesa': mesa.numero,
                'total': pedido.total,
                'estado': pedido.estado
            })

        # 👇 si viene de un formulario normal (no AJAX)
        messages.success(request, f"✅ Pedido #{pedido.id} creado para Mesa {mesa.numero}.")
        return redirect('mis_pedidos')

class MisPedidosView(LoginRequiredMixin, View):
    """Lista los pedidos del mesero actual."""
    def get(self, request):
        pedidos = Pedido.objects.filter(
            mesero=request.user
        ).select_related('mesa').prefetch_related('detallepedido_set__plato')
        empleado = Empleado.objects.filter(user=request.user).first()

        return render(request, 'panel/mis_pedidos.html', {
            'pedidos': pedidos,
            'empleado': empleado
        })


class CerrarPedidoView(LoginRequiredMixin, View):
    """Permite cerrar un pedido y liberar la mesa."""
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        pedido.estado = 'cerrado'
        pedido.save()

        pedido.mesa.ocupada = False
        pedido.mesa.save()

        messages.success(request, f"🧾 Pedido #{pedido.id} cerrado y Mesa {pedido.mesa.numero} liberada.")
        return redirect('mis_pedidos')
    


#========================================
#MESAS
#========================================

class PanelMesasView(LoginRequiredMixin, View):
    template_name = "panel/mesas.html"
    login_url = "/login/"

    def get(self, request):
        # 👇 Agregá esta línea:
        empleado = Empleado.objects.get(user=request.user)

        mesas = Mesa.objects.all().order_by("numero")
        return render(request, self.template_name, {
            "mesas": mesas,
            "empleado": empleado  # 👈 agregado al contexto
        })

    def post(self, request):
        empleado = Empleado.objects.get(user=request.user)  # también aquí si recargás la vista
        numero = request.POST.get("numero")
        if numero and not Mesa.objects.filter(numero=numero).exists():
            Mesa.objects.create(numero=numero)
            messages.success(request, f"✅ Mesa {numero} agregada correctamente.")
        else:
            messages.error(request, "⚠️ Ese número de mesa ya existe o es inválido.")
        return redirect("panel_mesas")

def cambiar_estado_mesa(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    mesa.ocupada = not mesa.ocupada
    mesa.save()
    return JsonResponse({"success": True, "ocupada": mesa.ocupada})



from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Empleado

class InicioView(LoginRequiredMixin, View):
    """Redirige según el rol del empleado después de iniciar sesión."""
    def get(self, request):
        empleado = Empleado.objects.filter(user=request.user).first()

        if empleado:
            if empleado.cargo == "administrador":
                return redirect("dashboard")
            elif empleado.cargo == "mesero":
                return redirect("mis_pedidos")

        # Si no tiene cargo asignado
        return redirect("mis_pedidos")
