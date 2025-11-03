from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView
from django.urls import reverse_lazy

from .models import Empleado
from .forms import EmpleadoModelForm

# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('panel_principal')  # cambiar por tu dashboard
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    
    return render(request, 'login.html')
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def panel_principal(request):
    return render(request, 'usuarios/panel.html')

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


from django.views.generic import DetailView, DeleteView
from django.urls import reverse_lazy


class EmpleadoCreateView(LoginRequiredMixin, CreateView):
    model = Empleado
    form_class = EmpleadoModelForm
    template_name = 'empleados_form.html'
    success_url = reverse_lazy('empleados')
    login_url = 'login'

    def form_valid(self, form):
        empleado = form.save()
        messages.success(self.request, f'Empleado creado correctamente (id: {empleado.pk}).')
        return super().form_valid(form)


class EmpleadoUpdateView(LoginRequiredMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoModelForm
    template_name = 'empleados_form.html'
    success_url = reverse_lazy('empleados')
    login_url = 'login'

    def form_valid(self, form):
        empleado = form.save()
        messages.success(self.request, f'Empleado {empleado.pk} actualizado correctamente.')
        return super().form_valid(form)


class EmpleadoDeleteView(LoginRequiredMixin, DeleteView):
    model = Empleado
    template_name = 'empleados_confirm_delete.html'
    success_url = reverse_lazy('empleados')
    login_url = 'login'