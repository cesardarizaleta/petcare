<script setup>
  import { onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';

  const appStore = useAppStore();
  const toastStore = useToastStore();

  onMounted(async () => {
    await appStore.fetchAppointmentsToday();
  });

  async function handleConfirm(appointment) {
    try {
      await appStore.confirmAppointment(appointment.id);
      toastStore.push({
        title: 'Cita confirmada',
        description: `${appointment.petName || 'Paciente'} fue confirmado/a.`,
        type: 'success',
      });
    } catch (e) {
      toastStore.push({ title: 'Error al confirmar', type: 'error' });
    }
  }

  async function handleCheckIn(appointment) {
    try {
      await appStore.checkInAppointment(appointment.id);
      toastStore.push({
        title: 'Check-in realizado',
        description: `${appointment.petName || 'Paciente'} pasó a sala de espera.`,
        type: 'success',
      });
    } catch (e) {
      toastStore.push({ title: 'Error en check-in', type: 'error' });
    }
  }

  async function handleCancel(appointment) {
    try {
      await appStore.cancelAppointment(appointment.id);
      toastStore.push({
        title: 'Cita cancelada',
        description: `${appointment.petName || 'Paciente'} fue cancelada.`,
        type: 'info',
      });
    } catch (e) {
      toastStore.push({ title: 'Error al cancelar', type: 'error' });
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
                  @click="handleConfirm(appointment)"
                >
                  Confirmar
                </button>
                <button
                  v-if="appointment.status === 'confirmed' || appointment.status === 'scheduled'"
                  class="btn btn--soft"
                  type="button"
                  @click="handleCheckIn(appointment)"
                >
                  Check-in
                </button>
                <button
                  v-if="appointment.status !== 'completed' && appointment.status !== 'cancelled'"
                  class="btn btn--soft"
                  type="button"
                  @click="handleCancel(appointment)"
                >
                  Cancelar
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
