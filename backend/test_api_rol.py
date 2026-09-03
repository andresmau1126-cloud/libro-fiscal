#!/usr/bin/env python
"""Test para verificar el cambio de rol via API"""
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

# Crear una sesión de admin válida
admin = Usuario.objects.filter(rol='admin').first()
if not admin:
    print("No hay admin disponible")
    exit(1)

# Crear una sesión para el admin
token = "test-token-" + secrets.token_hex(16)
session = Sesion.objects.create(
    usuario=admin,
    token=token,
    expires_at=timezone.now() + timedelta(days=1)
)

# Obtener el usuario mauricio1126@gmail.com
target_user = Usuario.objects.get(email='mauricio1126@gmail.com')
print(f"Usuario target: {target_user.email}, rol actual: {target_user.rol}")

# Hacer una prueba de actualización directa
print("\n--- Test 1: Actualización directa en BD ---")
target_user.rol = 'vendedor_2'
target_user.save()
target_user.refresh_from_db()
print(f"Rol después de guardar directamente: {target_user.rol}")

# Revertir al rol original
target_user.rol = 'admin'
target_user.save()

# Hacer una prueba via API usando requests
print("\n--- Test 2: Actualización via API REST ---")
BASE_URL = "http://127.0.0.1:8000/api"
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

payload = {
    'nombre': target_user.nombre,
    'email': target_user.email,
    'rol': 'vendedor_2'
}

print(f"Enviando: {json.dumps(payload)}")
print(f"URL: PUT {BASE_URL}/auth/usuarios/{target_user.id}/")

try:
    response = requests.put(
        f"{BASE_URL}/auth/usuarios/{target_user.id}/",
        json=payload,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        target_user.refresh_from_db()
        print(f"Rol después de API: {target_user.rol}")
except Exception as e:
    print(f"Error: {e}")

# Limpiar sesión de prueba
session.delete()
