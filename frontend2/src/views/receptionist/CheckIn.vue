<script setup>
  import { onMounted, reactive } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { useConfirmStore } from '@/stores/useConfirmStore';
  import { extractApiError } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const confirmStore = useConfirmStore();
  const loadingAppointments = reactive({});

  onMounted(async () => {
    await appStore.fetchAppointmentsToday();
  });

  async function handleConfirm(appointment) {
    const isConfirmed = await confirmStore.confirm({
      title: 'Confirmar Cita',
      message: `¿Estás seguro de que deseas confirmar la cita de ${appointment.petName || 'este paciente'} a las ${appointment.time}?`,
      confirmText: 'Confirmar',
      cancelText: 'Volver',
      type: 'success',
    });

    if (!isConfirmed) return;

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
    const isConfirmed = await confirmStore.confirm({
      title: 'Registrar Check-in',
      message: `¿Deseas registrar la llegada de ${appointment.petName || 'este paciente'} a la sala de espera?`,
      confirmText: 'Registrar llegada',
      cancelText: 'Volver',
      type: 'info',
    });

    if (!isConfirmed) return;

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
    const isConfirmed = await confirmStore.confirm({
      title: 'Cancelar Cita',
      message: `¿Estás completamente seguro de que deseas cancelar la cita de ${appointment.petName || 'este paciente'}? Esta acción no se puede deshacer.`,
      confirmText: 'Sí, cancelar cita',
      cancelText: 'No, mantener cita',
      type: 'danger',
    });

    if (!isConfirmed) return;

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

    <!-- Guía de Estados Breve -->
    <div class="status-legend card">
      <h3 class="status-legend__title">Guía rápida de estados de citas</h3>
      <div class="status-legend__grid">
        <div class="status-legend__item">
          <span class="chip chip--brand">Programada</span>
          <p class="status-legend__text">Agendada por el dueño, pendiente de confirmación.</p>
        </div>
        <div class="status-legend__item">
          <span class="chip chip--success">Confirmada</span>
          <p class="status-legend__text">Cita confirmada por el dueño. Lista para el ingreso.</p>
        </div>
        <div class="status-legend__item">
          <span class="chip chip--cream">Chequeada</span>
          <p class="status-legend__text">El paciente llegó a recepción y pasó a la sala de espera.</p>
        </div>
        <div class="status-legend__item">
          <span class="chip chip--warning">En Consulta</span>
          <p class="status-legend__text">El paciente se encuentra en atención con el veterinario.</p>
        </div>
        <div class="status-legend__item">
          <span class="chip chip--sage">Completada</span>
          <p class="status-legend__text">Cita finalizada con historia clínica ya registrada.</p>
        </div>
        <div class="status-legend__item">
          <span class="chip chip--danger">Cancelada</span>
          <p class="status-legend__text">Cita anulada; el horario quedó liberado.</p>
        </div>
      </div>
    </div>

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

<style scoped>
.status-legend {
  padding: 16px;
  background: var(--surface-soft, #f7f1e6);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg, 12px);
  margin-bottom: 8px;
}

.status-legend__title {
  font-family: var(--sans, sans-serif);
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: var(--text-strong, #171717);
}

.status-legend__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.status-legend__item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-legend__item .chip {
  flex-shrink: 0;
  width: 95px;
  text-align: center;
  font-size: 0.78rem;
  font-weight: 600;
}

.status-legend__text {
  font-family: var(--sans, sans-serif);
  font-size: 0.82rem;
  color: var(--text, #3d3d3d);
  margin: 0;
  line-height: 1.3;
}

@media (max-width: 600px) {
  .status-legend__grid {
    grid-template-columns: 1fr;
  }
}
</style>
