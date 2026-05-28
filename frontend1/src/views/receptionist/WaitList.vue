<script setup>
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { getTodayAppointments, getPet, getVet } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();

  function moveToFront(appointment) {
    appStore.updateAppointment({ ...appointment, status: 'confirmed' });
    toastStore.push({
      title: 'Paciente atendido',
      description: `${appointment.reason} pasó a confirmado.`,
      type: 'info',
    });
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Lista de Espera"
      subtitle="Pacientes pendientes por atender dentro del turno actual."
    />

    <section class="card">
      <div class="list">
        <article
          v-for="(appointment, index) in getTodayAppointments(appStore.appointments).filter(
            (item) => ['waiting', 'in_progress'].includes(item.status)
          )"
          :key="appointment.id"
          class="list__item"
          :style="appointment.status === 'confirmed' ? 'border-left: 4px solid var(--color-success);' : ''"
        >
          <div class="toolbar__group">
            <span class="chip chip--brand">P{{ index + 1 }}</span>
            <span 
              v-if="appointment.type === 'Emergencia'" 
              class="chip chip--danger" 
              style="font-size: 0.75rem;"
            >
              {{ appointment.priority }}
            </span>
            <PetAvatar :pet="getPet(appStore.pets, appointment.petId)" size="sm" />
            <div class="list__item-main">
              <p class="list__title">{{ getPet(appStore.pets, appointment.petId)?.name }}</p>
              <p class="list__subtitle">
                {{ appointment.reason }} · {{ getVet(appStore.vets, appointment.vetId)?.name }}
              </p>
            </div>
          </div>
          <div class="toolbar__group">
            <StatusBadge :status="appointment.status" />
            <button 
              v-if="appointment.status !== 'in_progress'"
              class="btn btn--soft btn--sm" 
              style="padding: 6px 12px; font-size: 0.8rem;"
              type="button" 
              @click="moveToFront(appointment)"
            >
              Pasar a consulta
            </button>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
