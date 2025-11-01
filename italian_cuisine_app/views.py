from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# Create your views here.
class VistaLogin(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('panel_principal')

    def get_success_url(self):
        return self.success_url