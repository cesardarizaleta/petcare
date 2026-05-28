<script setup>
  import { computed, ref, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import { useAppStore } from '@/stores/useAppStore';

  const appStore = useAppStore();
  const selectedAppointmentId = ref('');

  onMounted(async () => {
    await appStore.fetchAppointmentsToday();
  });

  const patients = computed(() => appStore.appointments);

  const selectedAppointment = computed(
    () =>
      patients.value.find((appointment) => appointment.id === selectedAppointmentId.value) ||
      patients.value[0] ||
      null
  );
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Pacientes del Día"
      subtitle="Pacientes asignados al veterinario para la jornada actual."
    />

    <section class="split">
      <DashboardCard title="Lista de pacientes" icon="dog">
        <div class="list">
          <button
            v-for="appointment in patients"
            :key="appointment.id"
            class="list__item"
            type="button"
            @click="selectedAppointmentId = appointment.id"
          >
            <div class="toolbar__group">
              <div class="list__item-main">
                <p class="list__title">
                  {{ appointment.time }} · {{ appointment.petName || 'Paciente' }}
                </p>
                <p class="list__subtitle">{{ appointment.reason }}</p>
              </div>
            </div>
            <StatusBadge :status="appointment.status" />
          </button>
          <p v-if="!patients.length" class="muted">No hay pacientes para hoy.</p>
        </div>
      </DashboardCard>

      <DashboardCard v-if="selectedAppointment" title="Detalle" icon="clipboard-list">
        <div class="stack">
          <div class="hero-intro">
            <p class="eyebrow">Veterinario</p>
            <h2 class="hero-intro__title">
              {{ selectedAppointment.vetName || 'Veterinario' }}
            </h2>
            <p class="hero-intro__text">{{ selectedAppointment.reason }}</p>
          </div>
          <div class="list__item">
            <div class="toolbar__group">
              <div class="list__item-main">
                <p class="list__title">
                  {{ selectedAppointment.petName || 'Paciente' }}
                </p>
                <p class="list__subtitle">
                  Propietario: {{ selectedAppointment.ownerName || '—' }}
                </p>
                <p class="list__subtitle">
                  Hora: {{ selectedAppointment.time }} · Estado: {{ selectedAppointment.status }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </DashboardCard>
    </section>
  </div>
</template>
