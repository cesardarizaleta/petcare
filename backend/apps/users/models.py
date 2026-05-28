from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        
        if 'username' not in extra_fields or not extra_fields.get('username'):
            extra_fields['username'] = email.split('@')[0]
            
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class NaturalPerson(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='natural_person')
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Datos de {self.user.email}"


class ClinicalStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='clinical_staff')
    natural_person = models.OneToOneField(NaturalPerson, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Staff - {self.user.email}"


class Veterinarian(models.Model):
    clinical_staff = models.OneToOneField(ClinicalStaff, on_delete=models.CASCADE, related_name='veterinarian')
    specialty = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Veterinarian - {self.clinical_staff.user.email}"


# --- MODELOS AÑADIDOS POR EL MÓDULO DE SEGURIDAD ---

class Supply(models.Model):
    name = models.CharField(max_length=150, verbose_name='nombre')
    current_stock = models.IntegerField(default=0, verbose_name='stock actual')

    class Meta:
        verbose_name = 'insumo'
        verbose_name_plural = 'insumos'

    def __str__(self):
        return f"{self.name} - Stock: {self.current_stock}"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='usuario')
    action = models.CharField(max_length=10, verbose_name='acción') 
    path = models.CharField(max_length=255, verbose_name='ruta')  
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='fecha')
    details = models.TextField(null=True, blank=True, verbose_name='detalles') 

    class Meta:
        verbose_name = 'registro de auditoría'
        verbose_name_plural = 'registros de auditoría'

    def __str__(self):
        nombre_usuario = self.user.email if self.user else "Anónimo"
        return f"{nombre_usuario} hizo {self.action} en {self.path} a las {self.timestamp}"


class SystemGroups:
    """
    Clase para obtener o crear los grupos de forma segura
    sin romper las migraciones de Django.
    """
    @property
    def owner(self):
        group, _ = Group.objects.get_or_create(name="owner")
        return group

    @property
    def receptionist(self):
        group, _ = Group.objects.get_or_create(name="receptionist")
        return group

groups = SystemGroups()
