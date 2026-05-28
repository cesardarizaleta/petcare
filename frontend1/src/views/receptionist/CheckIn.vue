<script setup>
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { getTodayAppointments, getPet, getVet, statusMeta } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();

  function setStatus(appointment, status) {
    appStore.updateAppointment({ ...appointment, status });
    toastStore.push({
      title: 'Estado actualizado',
      description: `${appointment.reason} cambió a ${statusMeta[status]?.label.toLowerCase() || status}.`,
      type: 'success',
    });
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
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="appointment in getTodayAppointments(appStore.appointments)"
            :key="appointment.id"
            class="table__row"
          >
            <td>
              <div class="toolbar__group">
                <PetAvatar :pet="getPet(appStore.pets, appointment.petId)" size="sm" />
                <div class="list__item-main">
                  <p class="list__title">{{ getPet(appStore.pets, appointment.petId)?.name }}</p>
                  <p class="list__subtitle">{{ appointment.reason }}</p>
                </div>
              </div>
            </td>
            <td>{{ appointment.time }}</td>
            <td>{{ getVet(appStore.vets, appointment.vetId)?.name }}</td>
            <td>
              <select class="select" style="min-width: 140px; padding: 6px 12px;" :value="appointment.status" @change="setStatus(appointment, $event.target.value)">
                <option value="scheduled">Programada</option>
                <option value="waiting">En Espera</option>
                <option value="confirmed">Confirmada</option>
                <option value="in_progress">En Consulta</option>
                <option value="completed">Completada</option>
                <option value="cancelled">Cancelada</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>
