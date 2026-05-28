<script setup>
  import { computed } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import {
    formatDate,
    getLatestConsultation,
    getLatestDeworming,
    getLatestVaccine,
    getOwnerPets,
  } from '@/lib/petcare';

  const appStore = useAppStore();
  const pets = computed(() => getOwnerPets(appStore.pets, appStore.currentUserId));
  const consultations = computed(() =>
    pets.value.flatMap((pet) => appStore.consultations.filter((item) => item.petId === pet.id))
  );
  const vaccines = computed(() =>
    pets.value.flatMap((pet) => appStore.vaccines.filter((item) => item.petId === pet.id))
  );
  const dewormings = computed(() =>
    pets.value.flatMap((pet) => appStore.dewormings.filter((item) => item.petId === pet.id))
  );
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Historial"
      subtitle="Consultas, vacunas y tratamientos anteriores del propietario."
    />

    <section class="grid grid--3">
      <DashboardCard title="Consultas" icon="stethoscope">
        <div class="list">
          <article v-for="item in consultations" :key="item.id" class="list__item">
            <div class="list__item-main">
              <p class="list__title">{{ formatDate(item.date) }}</p>
              <p class="list__subtitle">{{ item.diagnosis }}</p>
            </div>
            <StatusBadge status="completed" />
          </article>
        </div>
      </DashboardCard>

      <DashboardCard title="Vacunas" icon="syringe">
        <div class="list">
          <article v-for="item in vaccines" :key="item.id" class="list__item">
            <div class="list__item-main">
              <p class="list__title">{{ item.name }}</p>
              <p class="list__subtitle">Próxima: {{ formatDate(item.nextDate) }}</p>
            </div>
            <span class="chip chip--sage">{{ item.lot }}</span>
          </article>
        </div>
      </DashboardCard>

      <DashboardCard title="Desparasitaciones" icon="worm">
        <div class="list">
          <article v-for="item in dewormings" :key="item.id" class="list__item">
            <div class="list__item-main">
              <p class="list__title">{{ item.product }}</p>
              <p class="list__subtitle">Próxima: {{ formatDate(item.nextDate) }}</p>
            </div>
            <span class="chip chip--cream">{{ item.weight }} kg</span>
          </article>
        </div>
      </DashboardCard>
    </section>

    <section class="card">
      <div class="toolbar">
        <h2 class="section__title">Mascotas con seguimiento</h2>
      </div>
      <div class="list" style="margin-top: 16px">
        <article v-for="pet in pets" :key="pet.id" class="list__item">
          <div class="toolbar__group">
            <PetAvatar :pet="pet" size="sm" />
            <div class="list__item-main">
              <p class="list__title">{{ pet.name }}</p>
              <p class="list__subtitle">{{ pet.breed }} · {{ pet.color }}</p>
            </div>
          </div>
          <div class="toolbar__group">
            <span class="chip chip--brand"
              >Consulta:
              {{
                getLatestConsultation(appStore.consultations, pet.id)?.date
                  ? formatDate(getLatestConsultation(appStore.consultations, pet.id).date)
                  : 'Sin datos'
              }}</span
            >
            <span class="chip chip--sage"
              >Vacuna:
              {{
                getLatestVaccine(appStore.vaccines, pet.id)?.date
                  ? formatDate(getLatestVaccine(appStore.vaccines, pet.id).date)
                  : 'Sin datos'
              }}</span
            >
            <span class="chip chip--cream"
              >Desparasitación:
              {{
                getLatestDeworming(appStore.dewormings, pet.id)?.date
                  ? formatDate(getLatestDeworming(appStore.dewormings, pet.id).date)
                  : 'Sin datos'
              }}</span
            >
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
