#!/usr/bin/env python
"""Test simple para verificar PUT usuario"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.usuarios.models import Usuario
from apps.usuarios.serializers import UsuarioUpdateSerializer

# Obtener usuario
user = Usuario.objects.get(email='mauricio1126@gmail.com')
print(f"Usuario: {user.email}")
print(f"Rol actual: {user.rol}")

# Simular lo que hace el endpoint
data = {
    'nombre': user.nombre,
    'email': user.email,
    'rol': 'vendedor_2'
}

print(f"\nDatos a validar: {data}")

# Validar con serializer
serializer = UsuarioUpdateSerializer(data=data)
if serializer.is_valid():
    print("✓ Serializer válido")
    validated = serializer.validated_data
    print(f"Datos validados: {validated}")
    
    # Aplicar cambios como lo hace el endpoint
    if "nombre" in validated:
        user.nombre = validated["nombre"].strip()
    if "email" in validated:
        user.email = validated["email"].strip().lower()
    if "rol" in validated:
        print(f"  Cambiando rol de {user.rol} a {validated['rol']}")
        user.rol = validated["rol"]
    if "activo" in validated:
        user.activo = validated["activo"]
    if "password" in validated:
        user.set_password(validated["password"])
    
    print(f"\nAntes de guardar:")
    print(f"  user.rol = {user.rol}")
    user.save()
    print(f"✓ Usuario guardado")
    
    user.refresh_from_db()
    print(f"\nDespués de guardar:")
    print(f"  user.rol = {user.rol}")
else:
    print("✗ Serializer inválido")
    print(f"Errores: {serializer.errors}")
