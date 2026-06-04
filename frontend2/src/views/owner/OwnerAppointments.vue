<script setup>
  import { computed, ref, onMounted, reactive, watch } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { useConfirmStore } from '@/stores/useConfirmStore';
  import { formatDate, getOwnerAppointments, getPet } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const confirmStore = useConfirmStore();
  const cancellingAppointments = reactive({});

  const itemsPerPage = 5;
  const currentPage = ref(1);

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchProfile(),
        appStore.fetchPets(),
        appStore.fetchAppointments()
      ]);
    } catch (err) {
      console.error('Error fetching owner appointments data:', err);
    }
  });
  const activeFilter = ref('all');

  const filteredAppointments = computed(() => {
    const appointments = getOwnerAppointments(appStore.appointments, appStore.currentUserId);

    if (activeFilter.value === 'all') return appointments;
    if (activeFilter.value === 'upcoming')
      return appointments.filter(
        (item) =>
          item.status === 'scheduled' || item.status === 'confirmed' || item.status === 'waiting'
      );
    return appointments.filter((item) => item.status === activeFilter.value);
  });

  const totalPages = computed(() => Math.ceil(filteredAppointments.value.length / itemsPerPage));

  const paginatedAppointments = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage;
    return filteredAppointments.value.slice(start, start + itemsPerPage);
  });

  watch(activeFilter, () => {
    currentPage.value = 1;
  });

  function canCancel(appointment) {
    if (['completed', 'cancelled', 'checked_in'].includes(appointment.status.toLowerCase())) {
      return false;
    }
    const apptDateTime = new Date(`${appointment.date}T${appointment.time}`);
    const now = new Date();
    return apptDateTime > now;
  }

  async function cancelAppointment(appointment) {
    const isConfirmed = await confirmStore.confirm({
      title: 'Cancelar Cita',
      message: `¿Estás seguro de que deseas cancelar tu cita para el ${formatDate(appointment.date)} a las ${appointment.time}? Esta acción no se puede deshacer.`,
      confirmText: 'Sí, cancelar cita',
      cancelText: 'No, mantener cita',
      type: 'danger',
    });

    if (!isConfirmed) return;

    cancellingAppointments[appointment.id] = true;
    try {
      await appStore.cancelAppointment(appointment.id);
      toastStore.push({
        title: 'Cita cancelada',
        description: `${appointment.reason} fue cancelada.`,
        type: 'info',
      });
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.error || 'No se pudo cancelar la cita.';
      toastStore.push({
        title: 'Error al cancelar',
        description: detail,
        type: 'error',
      });
    } finally {
      delete cancellingAppointments[appointment.id];
    }
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Mis Citas"
      subtitle="Listado de citas del propietario con filtros por estado y acciones rápidas."
    />

    <div class="toolbar">
      <div class="toolbar__group">
        <button
          class="btn btn--ghost"
          :class="{ 'btn--primary': activeFilter === 'all' }"
          @click="activeFilter = 'all'"
        >
          Todas
        </button>
        <button
          class="btn btn--ghost"
          :class="{ 'btn--primary': activeFilter === 'upcoming' }"
          @click="activeFilter = 'upcoming'"
        >
          Próximas
        </button>
        <button
          class="btn btn--ghost"
          :class="{ 'btn--primary': activeFilter === 'completed' }"
          @click="activeFilter = 'completed'"
        >
          Completadas
        </button>
        <button
          class="btn btn--ghost"
          :class="{ 'btn--primary': activeFilter === 'cancelled' }"
          @click="activeFilter = 'cancelled'"
        >
          Canceladas
        </button>
      </div>
    </div>

    <section class="card table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Mascota</th>
            <th>Motivo</th>
            <th>Veterinario</th>
            <th>Estado</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr v-for="appointment in paginatedAppointments" :key="appointment.id" class="table__row">
            <td>{{ formatDate(appointment.date) }} · {{ appointment.time }}</td>
            <td>{{ getPet(appStore.pets, appointment.petId)?.name }}</td>
            <td>{{ appointment.reason }}</td>
            <td>{{ appointment.vetName || 'Veterinario' }}</td>
            <td><StatusBadge :status="appointment.status" /></td>
            <td>
              <button
                v-if="canCancel(appointment)"
                class="btn btn--soft"
                type="button"
                :disabled="!!cancellingAppointments[appointment.id]"
                @click="cancelAppointment(appointment)"
              >
                {{ cancellingAppointments[appointment.id] ? 'Cancelando...' : 'Cancelar' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Controles de Paginación -->
      <div class="pagination-controls" v-if="totalPages > 1">
        <button
          class="btn btn--soft btn--sm"
          type="button"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          &larr; Anterior
        </button>
        <span class="pagination-info">
          Página <strong>{{ currentPage }}</strong> de <strong>{{ totalPages }}</strong>
        </span>
        <button
          class="btn btn--soft btn--sm"
          type="button"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          Siguiente &rarr;
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.pagination-info {
  font-family: var(--sans);
  font-size: 0.9rem;
  color: var(--text);
}

.btn--sm {
  padding: 6px 12px;
  font-size: 0.8rem;
}
</style>
