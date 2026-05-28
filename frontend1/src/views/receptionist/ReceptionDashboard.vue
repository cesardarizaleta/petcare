<script setup>
  import { computed } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatCard from '@/components/shared/StatCard.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import {
    formatDate,
    getAppointmentStats,
    getPet,
    getVet,
    getTodayAppointments,
    getTodayDate,
    getAppointmentsByVet,
    timeSlots,
  } from '@/lib/petcare';

  const appStore = useAppStore();
  const todayDate = computed(() => getTodayDate());
  const todayAppointments = computed(() => getTodayAppointments(appStore.appointments));
  const stats = computed(() => getAppointmentStats(todayAppointments.value));

  const vetAvailability = computed(() => {
    return appStore.vets.map(vet => {
      const vetAppointments = getAppointmentsByVet(todayAppointments.value, vet.id);
      const occupiedSlots = vetAppointments.map(a => a.time);
      const availableSlots = timeSlots.filter(t => !occupiedSlots.includes(t));
      return {
        vet,
        availableSlots,
      };
    });
  });
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Dashboard de Recepción"
      subtitle="Operaciones del día, agenda y acciones rápidas."
    />

    <section class="grid grid--4">
      <StatCard label="Programadas" :value="stats.scheduled" icon="calendar-days" />
      <StatCard
        label="Confirmadas"
        :value="stats.confirmed"
        icon="check-circle-2"
        tone-class="chip--sage"
      />
      <StatCard
        label="En consulta"
        :value="stats.in_progress"
        icon="stethoscope"
        tone-class="chip--warning"
      />
      <StatCard
        label="En espera"
        :value="stats.waiting"
        icon="hourglass"
        tone-class="chip--cream"
      />
    </section>

    <section class="split">
      <DashboardCard title="Agenda de hoy" icon="calendar-days">
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
                <p class="list__subtitle">
                  {{ appointment.reason }} · {{ getVet(appStore.vets, appointment.vetId)?.name }}
                </p>
              </div>
            </div>
            <div class="toolbar__group" style="gap: 0.5rem">
              <StatusBadge :status="appointment.status" />
              <button 
                v-if="appointment.status === 'scheduled'" 
                @click="appStore.updateAppointment({ ...appointment, status: 'confirmed' })" 
                class="btn-quick-action btn-confirm"
              >
                Confirmar
              </button>
              <button 
                v-if="appointment.status === 'confirmed'" 
                @click="appStore.updateAppointment({ ...appointment, status: 'waiting' })" 
                class="btn-quick-action btn-checkin"
              >
                Check-in
              </button>
            </div>
          </article>
        </div>
      </DashboardCard>

 <div class="stack">
        <DashboardCard title="Resumen operativo" icon="clipboard-list">
          <div class="stack">
            <div class="hero-intro">
              <p class="eyebrow">Fecha actual</p>
              <h2 class="hero-intro__title">{{ formatDate(todayDate) }}</h2>
              <p class="hero-intro__text">
                La recepción puede usar esta vista para confirmar citas, atender llegadas y
                administrar la lista de espera.
              </p>
            </div>
            <div class="summary-grid">
              <article class="card">
                <p class="eyebrow">Agenda</p>
                <strong>{{ todayAppointments.length }}</strong>
              </article>
              <article class="card">
                <p class="eyebrow">Pacientes</p>
                <strong>{{ todayAppointments.length }}</strong>
              </article>
              <article class="card">
                <p class="eyebrow">Consultorios</p>
                <strong>3</strong>
              </article>
            </div>
          </div>
        </DashboardCard>

        <DashboardCard title="Disponibilidad Veterinaria" icon="clock">
          <div class="stack">
            <article v-for="v in vetAvailability" :key="v.vet.id" class="card">
              <div class="toolbar__group" style="justify-content: space-between; margin-bottom: 0.5rem">
                <strong>{{ v.vet.name }}</strong>
                <span class="chip chip--sage">{{ v.availableSlots.length }} libres</span>
              </div>
              <div style="display: flex; flex-wrap: wrap; gap: 0.25rem">
                <span v-for="time in v.availableSlots" :key="time" class="chip chip--outline" style="font-size: 0.75rem">
                  {{ time }}
                </span>
                <p v-if="!v.availableSlots.length" class="muted" style="font-size: 0.8rem">Sin turnos disponibles hoy.</p>
              </div>
            </article>
          </div>
        </DashboardCard>
      </div>
    </section>
  </div>
</template>

<style scoped>
.btn-quick-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.35rem 0.8rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.btn-confirm {
  background: linear-gradient(135deg, #fdfbf7 0%, #fdf5e6 100%);
  color: #b8860b;
  border: 1px solid #fce8b2;
}

.btn-confirm:hover {
  background: linear-gradient(135deg, #fdf5e6 0%, #fae1a2 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(184, 134, 11, 0.15);
}

.btn-confirm:active {
  transform: translateY(0);
}

.btn-checkin {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.btn-checkin:hover {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(30, 64, 175, 0.15);
}

.btn-checkin:active {
  transform: translateY(0);
}
</style>
