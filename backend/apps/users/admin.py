from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, NaturalPerson, ClinicalStaff, Veterinarian, AuditLog

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
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

admin.site.register(User, CustomUserAdmin)
admin.site.register(NaturalPerson)
admin.site.register(ClinicalStaff)
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
