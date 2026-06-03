<script setup>
  import { computed, ref, onMounted, reactive } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { formatDate, getOwnerAppointments, getPet } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const cancellingAppointments = reactive({});

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

  function canCancel(appointment) {
    if (['completed', 'cancelled', 'checked_in'].includes(appointment.status.toLowerCase())) {
      return false;
    }
    const apptDateTime = new Date(`${appointment.date}T${appointment.time}`);
    const now = new Date();
    return apptDateTime > now;
  }

  async function cancelAppointment(appointment) {
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
          <tr v-for="appointment in filteredAppointments" :key="appointment.id" class="table__row">
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
    </section>
  </div>
</template>
