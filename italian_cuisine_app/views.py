from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView, TemplateView
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Empleado, Pedido
from .forms import EmpleadoModelForm

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
    next_page = reverse_lazy('login')  # ✅ vuelve al login después de cerrar sesión

# ---------- GESTIÓN DE EMPLEADOS (tu versión local) ----------
class UserListView(LoginRequiredMixin, ListView):
    model = Empleado
    template_name = 'empleados.html'
    context_object_name = 'empleados'
    paginate_by = 10  # muestra 10 empleados por página
    login_url = 'login'

class EmpleadoDetailView(LoginRequiredMixin, DetailView):
    model = Empleado
    template_name = 'empleados_detail.html'
    context_object_name = 'empleado'
    login_url = 'login'
    partial_template_name = 'partials/empleado_detail_partial.html'

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return [self.partial_template_name]
        return [self.template_name]

class EmpleadoCreateView(LoginRequiredMixin, CreateView):
    model = Empleado
    form_class = EmpleadoModelForm
    template_name = 'empleados_form.html'
    partial_template_name = 'partials/empleado_form_partial.html'
    success_url = reverse_lazy('empleados')
    login_url = 'login'

    def form_valid(self, form):
        empleado = form.save()
        messages.success(self.request, f'Empleado creado correctamente (id: {empleado.pk}).')
        # If request is AJAX, return JSON with rendered row so client can insert it
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            row_html = render_to_string('partials/empleado_row_partial.html', {'empleado': empleado, 'request': self.request})
            return JsonResponse({'success': True, 'action': 'create', 'html': row_html, 'pk': empleado.pk})
        return super().form_valid(form)

    def form_invalid(self, form):
        # For AJAX, return rendered partial with status 400 so client can replace modal body
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.partial_template_name, {'form': form, 'request': self.request, 'submit_label': 'Crear'})
            return HttpResponse(html, status=400)
        return super().form_invalid(form)

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return [self.partial_template_name]
        return [self.template_name]

class EmpleadoUpdateView(LoginRequiredMixin, UpdateView):
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

class EmpleadoDeleteView(LoginRequiredMixin, DeleteView):
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