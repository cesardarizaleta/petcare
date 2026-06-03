<script setup>
  import { onMounted, reactive } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { extractApiError } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const loadingAppointments = reactive({});

  onMounted(async () => {
    await appStore.fetchAppointmentsToday();
  });

  async function handleConfirm(appointment) {
    loadingAppointments[appointment.id] = 'confirm';
    try {
      await appStore.confirmAppointment(appointment.id);
      toastStore.push({
        title: 'Cita confirmada',
        description: `${appointment.petName || 'Paciente'} fue confirmado/a.`,
        type: 'success',
      });
    } catch (e) {
      toastStore.push({ title: 'Error al confirmar', description: extractApiError(e), type: 'error' });
    } finally {
      delete loadingAppointments[appointment.id];
    }
  }

  async function handleCheckIn(appointment) {
    loadingAppointments[appointment.id] = 'checkin';
    try {
      await appStore.checkInAppointment(appointment.id);
      toastStore.push({
        title: 'Check-in realizado',
        description: `${appointment.petName || 'Paciente'} pasó a sala de espera.`,
        type: 'success',
      });
    } catch (e) {
      toastStore.push({ title: 'Error en check-in', description: extractApiError(e), type: 'error' });
    } finally {
      delete loadingAppointments[appointment.id];
    }
  }

  async function handleCancel(appointment) {
    loadingAppointments[appointment.id] = 'cancel';
    try {
      await appStore.cancelAppointment(appointment.id);
      toastStore.push({
        title: 'Cita cancelada',
        description: `${appointment.petName || 'Paciente'} fue cancelada.`,
        type: 'info',
      });
    } catch (e) {
      toastStore.push({ title: 'Error al cancelar', description: extractApiError(e), type: 'error' });
    } finally {
      delete loadingAppointments[appointment.id];
    }
  }
</script>

<template>
  <div class="stack">
    <PageHeader title="Check-in" subtitle="Recepción y control de llegada de pacientes." />

    <section class="card table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>Paciente</th>
            <th>Hora</th>
            <th>Veterinario</th>
            <th>Estado</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="appointment in appStore.appointments"
            :key="appointment.id"
            class="table__row"
          >
            <td>
              <div class="list__item-main">
                <p class="list__title">{{ appointment.petName || 'Paciente' }}</p>
                <p class="list__subtitle">{{ appointment.reason }}</p>
              </div>
            </td>
            <td>{{ appointment.time }}</td>
            <td>{{ appointment.vetName || '—' }}</td>
            <td><StatusBadge :status="appointment.status" /></td>
            <td>
              <div class="toolbar__group">
                <button
                  v-if="appointment.status === 'scheduled'"
                  class="btn btn--soft"
                  type="button"
                  :disabled="!!loadingAppointments[appointment.id]"
                  @click="handleConfirm(appointment)"
                >
                  {{ loadingAppointments[appointment.id] === 'confirm' ? 'Confirmando...' : 'Confirmar' }}
                </button>
                <button
                  v-if="appointment.status === 'confirmed' || appointment.status === 'scheduled'"
                  class="btn btn--soft"
                  type="button"
                  :disabled="!!loadingAppointments[appointment.id]"
                  @click="handleCheckIn(appointment)"
                >
                  {{ loadingAppointments[appointment.id] === 'checkin' ? 'Registrando...' : 'Check-in' }}
                </button>
                <button
                  v-if="appointment.status !== 'completed' && appointment.status !== 'cancelled'"
                  class="btn btn--soft"
                  type="button"
                  :disabled="!!loadingAppointments[appointment.id]"
                  @click="handleCancel(appointment)"
                >
                  {{ loadingAppointments[appointment.id] === 'cancel' ? 'Cancelando...' : 'Cancelar' }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!appStore.appointments.length" class="muted" style="padding: 1rem;">No hay citas hoy.</p>
    </section>
  </div>
</template>
