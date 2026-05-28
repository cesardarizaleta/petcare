<script setup>
  import { computed, ref } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { formatDate, getOwnerAppointments, getPet, getVet } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
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

  function cancelAppointment(appointment) {
    appStore.cancelAppointment(appointment.id);
    toastStore.push({
      title: 'Cita cancelada',
      description: `${appointment.reason} fue cancelada.`,
      type: 'info',
    });
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
            <td>{{ getVet(appStore.vets, appointment.vetId)?.name }}</td>
            <td><StatusBadge :status="appointment.status" /></td>
            <td>
              <button
                v-if="appointment.status !== 'completed' && appointment.status !== 'cancelled'"
                class="btn btn--soft"
                type="button"
                @click="cancelAppointment(appointment)"
              >
                Cancelar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>
