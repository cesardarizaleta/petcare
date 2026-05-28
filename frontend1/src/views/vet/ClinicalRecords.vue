<script setup>
  import { computed, ref, onMounted, watch } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { formatDate, getPetConsultations, getPetVaccines, getPetDewormings } from '@/lib/petcare';

  const appStore = useAppStore();
  const selectedPetId = ref('');

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchPets(),
        appStore.fetchAppointments()
      ]);
    } catch (err) {
      console.error('Error loading clinical records page data:', err);
    }
  });

  watch(
    () => appStore.pets,
    (pets) => {
      if (pets.length && !selectedPetId.value) {
        selectedPetId.value = pets[0].id;
      }
    },
    { immediate: true, deep: true }
  );

  watch(
    selectedPetId,
    async (newPetId) => {
      if (newPetId) {
        try {
          await appStore.fetchMedicalRecord(newPetId);
        } catch (err) {
          console.error(`Error loading medical record for pet ${newPetId}:`, err);
        }
      }
    },
    { immediate: true }
  );

  const selectedPet = computed(
    () => appStore.pets.find((pet) => pet.id === selectedPetId.value) || null
  );
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Fichas Clínicas"
      subtitle="Historial clínico, vacunas y desparasitaciones por mascota."
    />

    <section class="split">
      <DashboardCard title="Pacientes" icon="clipboard-list">
        <div class="list">
          <button
            v-for="pet in appStore.pets"
            :key="pet.id"
            class="list__item"
            type="button"
            @click="selectedPetId = pet.id"
          >
            <div class="toolbar__group">
              <PetAvatar :pet="pet" size="sm" />
              <div class="list__item-main">
                <p class="list__title">{{ pet.name }}</p>
                <p class="list__subtitle">{{ pet.breed }}</p>
              </div>
            </div>
            <span class="chip chip--sage">{{ pet.species }}</span>
          </button>
        </div>
      </DashboardCard>

      <div class="stack" v-if="selectedPet">
        <section class="card">
          <div class="toolbar">
            <div class="toolbar__group">
              <PetAvatar :pet="selectedPet" size="lg" />
              <div>
                <h2 class="section__title">{{ selectedPet.name }}</h2>
                <p class="muted">{{ selectedPet.breed }} · {{ selectedPet.color }}</p>
              </div>
            </div>
          </div>
        </section>

        <DashboardCard title="Consultas" icon="stethoscope">
          <div class="list">
            <article
              v-for="item in getPetConsultations(appStore.consultations, selectedPet.id)"
              :key="item.id"
              class="list__item"
            >
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
            <article
              v-for="item in getPetVaccines(appStore.vaccines, selectedPet.id)"
              :key="item.id"
              class="list__item"
            >
              <div class="list__item-main">
                <p class="list__title">{{ item.name }}</p>
                <p class="list__subtitle">
                  {{ formatDate(item.date) }} · Próxima {{ formatDate(item.nextDate) }}
                </p>
              </div>
            </article>
          </div>
        </DashboardCard>

        <DashboardCard title="Desparasitaciones" icon="worm">
          <div class="list">
            <article
              v-for="item in getPetDewormings(appStore.dewormings, selectedPet.id)"
              :key="item.id"
              class="list__item"
            >
              <div class="list__item-main">
                <p class="list__title">{{ item.product }}</p>
                <p class="list__subtitle">
                  {{ formatDate(item.date) }} · Próxima {{ formatDate(item.nextDate) }}
                </p>
              </div>
            </article>
          </div>
        </DashboardCard>
      </div>
    </section>
  </div>
</template>
