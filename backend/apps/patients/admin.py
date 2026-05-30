from django.contrib import admin
from .models import Patient, ClinicalRecords, VaccinationPlan, VaccinationPlanItem, VaccinationDewormingEvent

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'species_breed', 'gender', 'birth_date', 'owner', 'microchip_id')
    search_fields = ('name', 'species_breed', 'microchip_id', 'owner__user__email')
    list_filter = ('gender', 'birth_date')

@admin.register(ClinicalRecords)
class ClinicalRecordsAdmin(admin.ModelAdmin):
    list_display = ('patient', 'opened_at')
    search_fields = ('patient__name', 'patient__microchip_id', 'medical_alerts')
    list_filter = ('opened_at',)

class VaccinationPlanItemInline(admin.TabularInline):
    model = VaccinationPlanItem
    extra = 1

@admin.register(VaccinationPlan)
class VaccinationPlanAdmin(admin.ModelAdmin):
    list_display = ('patient', 'vet', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('patient__name', 'vet__clinical_staff__user__email')
    inlines = [VaccinationPlanItemInline]

@admin.register(VaccinationDewormingEvent)
class VaccinationDewormingEventAdmin(admin.ModelAdmin):
    list_display = ('plan', 'event_type', 'vaccine_name_or_dewormer', 'applied_date', 'next_due_date')
    list_filter = ('event_type', 'applied_date')
    search_fields = ('plan__patient__name', 'sanitary_batch')

    def vaccine_name_or_dewormer(self, obj):
        return obj.dose
    vaccine_name_or_dewormer.short_description = 'Dosis/Insumo'
