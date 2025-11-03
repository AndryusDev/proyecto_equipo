from django.contrib.auth.models import User
from italian_cuisine_app.models import Empleado

username = 'Dilan'
email = 'dilandaniel.hc@gmail.com'
password = '123456'

u, created = User.objects.get_or_create(username=username, defaults={'email': email})
if created:
    u.set_password(password)
    u.save()
    print('User created:', username)
else:
    print('User already exists:', username)

emp, ec = Empleado.objects.get_or_create(user=u, defaults={'cargo': 'mesero'})
if ec:
    print('Empleado created for user:', username)
else:
    print('Empleado already exists for user:', username)

print('Done')
