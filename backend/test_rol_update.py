#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.usuarios.models import Usuario
from apps.usuarios.serializers import UsuarioUpdateSerializer

# Validar el serializer
data = {'rol': 'vendedor_2'}
serializer = UsuarioUpdateSerializer(data=data)
print('Valid:', serializer.is_valid())
print('Errors:', serializer.errors)
print('Validated data:', serializer.validated_data if serializer.is_valid() else 'N/A')

# Ahora intentar actualizar un usuario real
try:
    user = Usuario.objects.filter(email__icontains='mauricio').first()
    if user:
        print(f'\nUsuario encontrado: {user.email}, rol actual: {user.rol}')
        print('Intentando cambiar rol a vendedor_2...')
        user.rol = 'vendedor_2'
        user.save(update_fields=['rol'])
        user.refresh_from_db()
        print(f'Rol después de guardar: {user.rol}')
    else:
        print('Usuario mauricio1126@gmail.com no encontrado')
except Exception as e:
    print(f'Error: {e}')
