from django.urls import path
from .views import VistaLogin

urlpatterns = [
    path('login/', VistaLogin.as_view(), name='login'),
]
