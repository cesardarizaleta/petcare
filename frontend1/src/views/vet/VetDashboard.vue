<script setup>
  import { computed, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatCard from '@/components/shared/StatCard.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import {
    getAppointmentsByVet,
    getPet,
    getVet,
    getAppointmentStats,
    formatDate,
    getTodayShortDate,
  } from '@/lib/petcare';

  const appStore = useAppStore();

  onMounted(async () => {
    try {
      await appStore.fetchPets();
      await appStore.fetchAppointments();
    } catch (err) {
      console.error('Error loading veterinarian dashboard data:', err);
    }
  });

  const currentVetId = computed(() => appStore.currentUserId || 'v1');
  const vetAppointments = computed(() =>
    getAppointmentsByVet(appStore.appointments, currentVetId.value)
  );
  const todayAppointments = computed(() =>
    vetAppointments.value.filter((appointment) => appointment.date === getTodayShortDate())
  );
  const stats = computed(() => getAppointmentStats(todayAppointments.value));
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Agenda Veterinaria"
      subtitle="Vista del médico sobre pacientes, consultas y tareas del día."
    />

    <section class="grid grid--4">
      <StatCard label="Pacientes hoy" :value="todayAppointments.length" icon="dog" />
      <StatCard
        label="En consulta"
        :value="stats.in_progress"
        icon="stethoscope"
        tone-class="chip--warning"
      />
      <StatCard
        label="Confirmadas"
        :value="stats.confirmed"
        icon="check-circle-2"
        tone-class="chip--sage"
      />
      <StatCard
        label="Completadas"
        :value="stats.completed"
        icon="clipboard-list"
        tone-class="chip--cream"
      />
    </section>

    <section class="split">
      <DashboardCard title="Pacientes del día" icon="clipboard-list">
        <div class="list">
          <article
            v-for="appointment in todayAppointments"
            :key="appointment.id"
            class="list__item"
          >
            <div class="toolbar__group">
              <PetAvatar :pet="getPet(appStore.pets, appointment.petId)" size="sm" />
              <div class="list__item-main">
                <p class="list__title">
                  {{ appointment.time }} · {{ getPet(appStore.pets, appointment.petId)?.name }}
                  <span v-if="appointment.type === 'Emergencia'" class="chip chip--danger" style="margin-left: 8px; padding: 0.2rem 0.5rem; font-size: 0.7rem;">
                    Emergencia ({{ appointment.priority }})
                  </span>
                </p>
                <p class="list__subtitle">{{ appointment.reason }}</p>
              </div>
            </div>
            <StatusBadge :status="appointment.status" />
          </article>
        </div>
      </DashboardCard>

      <DashboardCard title="Estado de la agenda" icon="calendar-days">
        <div class="stack">
          <div class="hero-intro">
            <p class="eyebrow">Veterinario activo</p>
            <h2 class="hero-intro__title">
              {{ getVet(appStore.vets, currentVetId)?.name || 'Veterinario' }}
            </h2>
            <p class="hero-intro__text">
              La migración conserva el contexto por rol y la data clínica de cada mascota.
            </p>
          </div>
          <div class="summary-grid">
            <article class="card">
              <p class="eyebrow">Agenda</p>
              <strong>{{ vetAppointments.length }}</strong>
            </article>
            <article class="card">
              <p class="eyebrow">Hoy</p>
              <strong>{{ todayAppointments.length }}</strong>
            </article>
            <article class="card">
              <p class="eyebrow">Fecha</p>
              <strong>{{ formatDate(getTodayShortDate()) }}</strong>
            </article>
          </div>
        </div>
      </DashboardCard>
    </section>
  </div>
</template>
