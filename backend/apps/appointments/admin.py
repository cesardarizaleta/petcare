from django.contrib import admin
from .models import VetSchedule, TimeSlot, Appointment, WaitingListEntry

class TimeSlotInline(admin.TabularInline):
    model = TimeSlot
    extra = 4

@admin.register(VetSchedule)
class VetScheduleAdmin(admin.ModelAdmin):
    list_display = ('vet', 'start_date', 'end_date')
    search_fields = ('vet__clinical_staff__user__email', 'vet__clinical_staff__user__first_name')
    list_filter = ('start_date', 'end_date')
    inlines = [TimeSlotInline]

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'start_time')
    search_fields = ('schedule__vet__clinical_staff__user__email',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'slot', 'status', 'checked_in_at')
    list_filter = ('status', 'checked_in_at')
    search_fields = ('patient__name', 'reason_for_visit')

@admin.register(WaitingListEntry)
class WaitingListEntryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'priority_level', 'status')
    list_filter = ('priority_level', 'status')
    search_fields = ('patient__name',)
