<script setup>
  import { computed, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatCard from '@/components/shared/StatCard.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import {
    getAppointmentStats,
    formatDate,
    todayISO,
  } from '@/lib/petcare';

  const appStore = useAppStore();

  onMounted(async () => {
    await appStore.fetchAppointmentsToday();
  });

  const todayAppointments = computed(() => appStore.appointments);
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
              <div class="list__item-main">
                <p class="list__title">
                  {{ appointment.time }} · {{ appointment.petName || 'Paciente' }}
                </p>
                <p class="list__subtitle">{{ appointment.reason }}</p>
              </div>
            </div>
            <StatusBadge :status="appointment.status" />
          </article>
          <p v-if="!todayAppointments.length" class="muted">No hay pacientes para hoy.</p>
        </div>
      </DashboardCard>

      <DashboardCard title="Estado de la agenda" icon="calendar-days">
        <div class="stack">
          <div class="hero-intro">
            <p class="eyebrow">Fecha actual</p>
            <h2 class="hero-intro__title">{{ formatDate(todayISO()) }}</h2>
            <p class="hero-intro__text">
              Agenda del veterinario conectada en tiempo real al sistema PetCare.
            </p>
          </div>
          <div class="summary-grid">
            <article class="card">
              <p class="eyebrow">Total</p>
              <strong>{{ todayAppointments.length }}</strong>
            </article>
            <article class="card">
              <p class="eyebrow">En espera</p>
              <strong>{{ stats.waiting }}</strong>
            </article>
            <article class="card">
              <p class="eyebrow">Completadas</p>
              <strong>{{ stats.completed }}</strong>
            </article>
          </div>
        </div>
      </DashboardCard>
    </section>
  </div>
</template>
