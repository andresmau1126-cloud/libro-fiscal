#!/usr/bin/env python
"""Crear una sesión válida y hacer una petición PUT con requests"""
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.usuarios.models import Usuario, Sesion
from django.utils import timezone
from datetime import timedelta
import secrets

# Obtener admin
admin = Usuario.objects.filter(rol='admin').first()
user = Usuario.objects.get(email='mauricio1126@gmail.com')

# Crear una sesión válida para el admin
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
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

print(f"PUT {url}")
print(f"Authorization: Bearer {token[:20]}...")
print(f"Payload: {json.dumps(data)}")
print()

try:
    response = requests.put(url, json=data, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ Petición exitosa")
        result = response.json()
        print(f"Nuevo rol retornado: {result.get('rol')}")
    else:
        print(f"\n✗ Error en petición: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Verificar cambio
user.refresh_from_db()
print(f"\nRol en BD después: {user.rol}")

# Cleanup
sesion.delete()
