#!/usr/bin/env python
"""Crear una sesión válida y hacer una petición PUT"""
import os
import django
import subprocess
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.usuarios.models import Usuario, Sesion
from django.utils import timezone
from datetime import timedelta

# Obtener admin
admin = Usuario.objects.filter(rol='admin').first()
user = Usuario.objects.get(email='mauricio1126@gmail.com')

# Crear una sesión válida para el admin
import secrets
token = secrets.token_urlsafe(48)
hours = 24
expires = timezone.now() + timedelta(hours=hours)
Sesion.objects.filter(usuario=admin).delete()  # Limpiar sesiones viejas
sesion = Sesion.objects.create(
    usuario=admin,
    token=token,
    expires_at=expires,
)

print(f"Admin: {admin.email}")
print(f"Token de sesión: {token[:20]}...")
print(f"Usuario target: {user.email}, rol actual: {user.rol}")
print()

# Preparar los datos
data = {
    'nombre': user.nombre,
    'email': user.email,
    'rol': 'vendedor_2'
}

# Hacer petición PUT
url = f"http://127.0.0.1:8000/api/auth/usuarios/{user.id}/"
headers = f'Authorization: Bearer {token}'
json_data = json.dumps(data)

print(f"PUT {url}")
print(f"Authorization: Bearer {token[:20]}...")
print(f"Payload: {json_data}")
print()

cmd = [
    'curl',
    '-X', 'PUT',
    url,
    '-H', 'Content-Type: application/json',
    '-H', headers,
    '-d', json_data,
    '-v'
]

result = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)

# Verificar cambio
user.refresh_from_db()
print(f"\nRol en BD después: {user.rol}")

# Cleanup
sesion.delete()
