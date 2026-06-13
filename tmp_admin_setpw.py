import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
backend = root / 'backend'

sys.path.insert(0, str(backend))
os.chdir(backend)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.usuarios.models import Usuario

admin = Usuario.objects.filter(email='andresmau1126@gmail.com').first()
if admin:
    admin.set_password('Admin123!')
    admin.email_verified = True
    admin.save(update_fields=['password', 'email_verified'])
    print(admin.email)
else:
    print('admin-not-found')
