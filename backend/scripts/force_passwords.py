#!/usr/bin/env python
import os
import sys
from pathlib import Path
import django

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def force_passwords():
    emails = [
        'admin@petcare.com',
        'vet@petcare.com',
        'recepcion@petcare.com',
        'propietario@petcare.com',
        'tecnico@petcare.com'
    ]
    
    print("Iniciando actualización forzada de contraseñas...")
    for email in emails:
        try:
            user = User.objects.get(email=email)
            user.set_password('petcare123')
            user.save()
            print(f"Contraseña de {email} actualizada a 'petcare123' exitosamente.")
        except User.DoesNotExist:
            print(f"El usuario {email} no existe en la base de datos.")

if __name__ == '__main__':
    force_passwords()
