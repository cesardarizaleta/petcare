<script setup>
  import { computed, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatCard from '@/components/shared/StatCard.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import {
    formatDate,
    getLatestConsultation,
    getLatestDeworming,
    getLatestVaccine,
    getOwnerAppointments,
    getOwnerPets,
    getPet,
  } from '@/lib/petcare';

  const appStore = useAppStore();

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchProfile(),
        appStore.fetchPets(),
        appStore.fetchAppointments(),
      ]);
    } catch (err) {
      console.error('Error fetching owner dashboard data:', err);
    }
  });
  const currentOwner = computed(() => appStore.currentOwner);
  const ownerPets = computed(() => getOwnerPets(appStore.pets, appStore.currentUserId));
  const ownerAppointments = computed(() =>
    getOwnerAppointments(appStore.appointments, appStore.currentUserId)
  );
  const upcomingAppointments = computed(() =>
    ownerAppointments.value
      .filter(
        (appointment) => appointment.status !== 'completed' && appointment.status !== 'cancelled'
      )
      .slice(0, 3)
  );
  const completedAppointments = computed(
    () => ownerAppointments.value.filter((appointment) => appointment.status === 'completed').length
  );

  function petOverview(pet) {
    return {
      consultation: getLatestConsultation(appStore.consultations, pet.id),
      vaccine: getLatestVaccine(appStore.vaccines, pet.id),
      deworming: getLatestDeworming(appStore.dewormings, pet.id),
    };
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Portal Propietario"
      :subtitle="`Hola ${currentOwner?.name || 'propietario'}, este es el resumen de tus mascotas, citas y tratamientos.`"
    />

    <section class="grid grid--4">
      <StatCard
        label="Mascotas registradas"
        :value="ownerPets.length"
        icon="paw-print"
        tone-class="chip--brand"
      />
      <StatCard
        label="Citas próximas"
        :value="upcomingAppointments.length"
        icon="calendar-days"
        tone-class="chip--sage"
      />
      <StatCard
        label="Citas completadas"
        :value="completedAppointments"
        icon="check-circle-2"
        tone-class="chip--cream"
      />
      <StatCard
        label="Tratamientos activos"
        :value="ownerPets.length"
        icon="stethoscope"
        tone-class="chip--warning"
      />
    </section>

    <section class="split">
      <DashboardCard title="Próximas citas" icon="calendar-days">
        <div class="list">
          <article
            v-for="appointment in upcomingAppointments"
            :key="appointment.id"
            class="list__item"
          >
            <div class="list__item-main">
              <p class="list__title">{{ formatDate(appointment.date) }} · {{ appointment.time }}</p>
              <p class="list__subtitle">
                {{ getPet(appStore.pets, appointment.petId)?.name }} · {{ appointment.reason }}
              </p>
            </div>
            <StatusBadge :status="appointment.status" />
          </article>
          <p v-if="!upcomingAppointments.length" class="muted">No hay citas próximas por ahora.</p>
        </div>
      </DashboardCard>

      <DashboardCard title="Mascotas y seguimiento" icon="paw-print">
        <div class="list">
          <article v-for="pet in ownerPets" :key="pet.id" class="list__item">
            <div class="list__item-main">
              <div class="toolbar__group">
                <PetAvatar :pet="pet" size="sm" />
                <div>
                  <p class="list__title">{{ pet.name }}</p>
                  <p class="list__subtitle">{{ pet.breed }} · {{ pet.color }}</p>
                </div>
              </div>
              <p class="list__subtitle">
                Última consulta:
                {{
                  petOverview(pet).consultation
                    ? formatDate(petOverview(pet).consultation.date)
                    : 'Sin registros'
                }}
              </p>
            </div>
            <div class="stack" style="justify-items: end; gap: 8px">
              <span class="chip chip--sage">{{ pet.species }}</span>
            </div>
          </article>
        </div>
      </DashboardCard>
    </section>
  </div>
</template>
