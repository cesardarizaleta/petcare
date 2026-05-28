<script setup>
  import { computed, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import {
    formatDate,
    getLatestConsultation,
    getLatestVaccine,
    getOwnerPets,
  } from '@/lib/petcare';

  const appStore = useAppStore();
  const router = useRouter();

  onMounted(() => {
    appStore.fetchPets().catch((err) => console.error('Error fetching pets:', err));
  });
  
  const pets = computed(() => getOwnerPets(appStore.pets, appStore.currentUserId));

  function viewPet(pet) {
    router.push(`/portal/pets/${pet.id}`);
  }

  function editPet(pet) {
    router.push(`/portal/pets/${pet.id}/edit`);
  }
</script>

<template>
  <div class="stack">
    <div class="pets-header">
      <PageHeader title="Mis Mascotas" subtitle="Gestión de mascotas vinculadas al propietario." />
      <router-link to="/portal/pets/add" class="btn btn--primary">
        + Agregar Mascota
      </router-link>
    </div>

    <section>
      <DashboardCard title="Mascotas registradas" icon="paw-print">
        <div class="list">
          <article v-for="pet in pets" :key="pet.id" class="list__item">
            <div class="toolbar__group">
              <PetAvatar :pet="pet" size="sm" />
              <div class="list__item-main">
                <p class="list__title">{{ pet.name }}</p>
                <p class="list__subtitle">{{ pet.breed }} · {{ pet.color }}</p>
                <p class="list__subtitle">
                  Última consulta:
                  {{
                    getLatestConsultation(appStore.consultations, pet.id)?.date
                      ? formatDate(getLatestConsultation(appStore.consultations, pet.id).date)
                      : 'Sin consultas'
                  }}
                </p>
              </div>
            </div>
            <div class="stack pet-status">
              <span class="chip chip--sage">{{ pet.species === 'dog' ? 'Perro' : pet.species === 'cat' ? 'Gato' : pet.species === 'bird' ? 'Ave' : pet.species === 'rabbit' ? 'Conejo' : 'Otro' }}</span>
              <span class="muted"
                >Vacunas:
                {{ getLatestVaccine(appStore.vaccines, pet.id) ? 'Activas' : 'Sin datos' }}</span
              >
              <div class="pet-actions">
                <button class="btn btn--soft pet-action-btn" type="button" @click="viewPet(pet)">Ver detalle</button>
                <button class="btn btn--ghost pet-action-btn" type="button" @click="editPet(pet)">Editar</button>
              </div>
            </div>
          </article>
          <p v-if="!pets.length" class="muted">Todavía no hay mascotas asociadas.</p>
        </div>
      </DashboardCard>
    </section>
  </div>
</template>

<style scoped>
.pets-header {
  display: flex; 
  justify-content: space-between; 
  align-items: center;
}

.pet-status {
  justify-items: end;
  gap: 8px;
}

.pet-actions {
  display: flex; 
  gap: 8px;
}

.pet-action-btn {
  padding: 4px 12px; 
  font-size: 0.8rem;
}
</style>
