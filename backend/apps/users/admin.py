from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, NaturalPerson, ClinicalStaff, Veterinarian, AuditLog
from apps.owners.models import Owner

class NaturalPersonInline(admin.StackedInline):
    model = NaturalPerson
    can_delete = False
    max_num = 1
    verbose_name = "Datos Personales (Natural Person)"
    verbose_name_plural = "Datos Personales (Natural Person)"

class OwnerInline(admin.StackedInline):
    model = Owner
    can_delete = True
    max_num = 1
    verbose_name = "Perfil de Propietario (Owner)"
    verbose_name_plural = "Perfil de Propietario (Owner)"

class ClinicalStaffInline(admin.StackedInline):
    model = ClinicalStaff
    can_delete = True
    max_num = 1
    verbose_name = "Perfil de Personal Clínico (Clinical Staff)"
    verbose_name_plural = "Perfil de Personal Clínico (Clinical Staff)"

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = [NaturalPersonInline, OwnerInline, ClinicalStaffInline]
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        user = form.instance
        
        # 1. Asegurar que existe NaturalPerson para el usuario
        natural_person, _ = NaturalPerson.objects.get_or_create(user=user)
        
        # 2. Obtener los nombres de los grupos del usuario
        group_names = set(user.groups.values_list('name', flat=True))
        
        # 3. Si el usuario pertenece al grupo 'owner':
        if 'owner' in group_names:
            Owner.objects.get_or_create(
                user=user,
                defaults={
                    'natural_person': natural_person,
                    'location': 'Sede Palermo'
                }
            )
        else:
            Owner.objects.filter(user=user).delete()
            
        # 4. Si el usuario es de staff/veterinarian/receptionist/manager/technician:
        staff_roles = {'veterinarian', 'receptionist', 'manager', 'technician', 'veterinary_technician'}
        is_staff_role = bool(group_names & staff_roles) or user.is_staff or user.is_superuser
        
        if is_staff_role:
            clinical_staff, _ = ClinicalStaff.objects.get_or_create(
                user=user,
                defaults={'natural_person': natural_person}
            )
            if 'veterinarian' in group_names:
                Veterinarian.objects.get_or_create(
                    clinical_staff=clinical_staff,
                    defaults={'specialty': 'General'}
                )
            else:
                Veterinarian.objects.filter(clinical_staff=clinical_staff).delete()
        else:
            clinical_staff = ClinicalStaff.objects.filter(user=user).first()
            if clinical_staff:
                Veterinarian.objects.filter(clinical_staff=clinical_staff).delete()
                clinical_staff.delete()

class VeterinarianInline(admin.StackedInline):
    model = Veterinarian
    can_delete = False
    max_num = 1
    verbose_name = "Datos Veterinarios (Veterinarian Specialty)"
    verbose_name_plural = "Datos Veterinarios (Veterinarian Specialty)"

class CustomClinicalStaffAdmin(admin.ModelAdmin):
    inlines = [VeterinarianInline]

admin.site.register(User, CustomUserAdmin)
admin.site.register(NaturalPerson)
admin.site.register(ClinicalStaff, CustomClinicalStaffAdmin)
admin.site.register(Veterinarian)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'path')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'path', 'details')
    ordering = ('-timestamp',)
    
    # Audit logs should be read-only in the admin panel for integrity
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
