from django import forms
from .models import Empleado
from django.contrib.auth.models import User


class EmpleadoModelForm(forms.ModelForm):
    username = forms.CharField(label="Usuario", required=True)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, required=True)
    email = forms.EmailField(label="Correo electrónico", required=True)

    class Meta:
        model = Empleado
        fields = ['first_name', 'last_name', 'cargo', 'telefono']

    def save(self, commit=True):
        # Crear usuario primero
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        email = self.cleaned_data.get('email')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        empleado = super().save(commit=False)
        empleado.user = user  # Asocia el user al empleado
        if commit:
            empleado.save()
        return empleado

