<script setup>
  import { computed, ref, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import {
    formatDate,
    getPet,
    getPetConsultations,
    getPetVaccines,
    getPetDewormings,
  } from '@/lib/petcare';

  const appStore = useAppStore();
  const route = useRoute();
  const router = useRouter();

  const selectedPet = ref(null);

  onMounted(() => {
    const pet = getPet(appStore.pets, route.params.id);
    if (pet) {
      selectedPet.value = pet;
    } else {
      router.push('/portal/pets');
    }
  });

  const selectedPetConsultations = computed(() => 
    selectedPet.value ? getPetConsultations(appStore.consultations, selectedPet.value.id) : []
  );
  const selectedPetVaccines = computed(() => 
    selectedPet.value ? getPetVaccines(appStore.vaccines, selectedPet.value.id) : []
  );
  const selectedPetDewormings = computed(() => 
    selectedPet.value ? getPetDewormings(appStore.dewormings, selectedPet.value.id) : []
  );

  function goBack() {
    router.push('/portal/pets');
  }

  function editPet() {
    router.push(`/portal/pets/${selectedPet.value.id}/edit`);
  }
</script>

<template>
  <div class="stack" v-if="selectedPet">
    <div class="header-with-actions">
      <PageHeader 
        :title="`Historial Médico de ${selectedPet.name}`" 
        subtitle="Consulta todos los registros, vacunas y detalle clínico." 
      />
      <div style="display: flex; gap: 8px;">
        <button class="btn btn--ghost" type="button" @click="goBack">Volver</button>
        <button class="btn btn--primary" type="button" @click="editPet">Editar Datos</button>
      </div>
    </div>

    <section class="card detail-container">
      <div class="stack" style="gap: 20px;">
        <div class="pet-header-info">
          <PetAvatar :pet="selectedPet" size="lg" style="width: 80px; height: 80px;" />
          <div>
            <h3 class="pet-name">{{ selectedPet.name }}</h3>
            <p class="pet-summary">
              {{ selectedPet.breed }} · {{ selectedPet.sex === 'M' ? 'Macho' : 'Hembra' }}
            </p>
          </div>
        </div>

        <div class="input-grid">
          <div>
            <p class="eyebrow">Especie</p>
            <p class="pet-data">{{ selectedPet.species === 'dog' ? 'Perro' : selectedPet.species === 'cat' ? 'Gato' : selectedPet.species === 'bird' ? 'Ave' : selectedPet.species === 'rabbit' ? 'Conejo' : 'Otro' }}</p>
          </div>
          <div>
            <p class="eyebrow">Fecha de nacimiento</p>
            <p class="pet-data">{{ formatDate(selectedPet.birthDate) }}</p>
          </div>
          <div>
            <p class="eyebrow">Peso</p>
            <p class="pet-data">{{ selectedPet.weight ? `${selectedPet.weight} kg` : 'No registrado' }}</p>
          </div>
          <div>
            <p class="eyebrow">Color</p>
            <p class="pet-data">{{ selectedPet.color || 'No registrado' }}</p>
          </div>
        </div>

        <div v-if="selectedPet.notes">
          <p class="eyebrow">Notas</p>
          <p class="pet-notes">
            {{ selectedPet.notes }}
          </p>
        </div>

        <div>
          <h4 class="history-title">Historial Clínico</h4>
          
          <div v-if="selectedPetConsultations.length > 0" class="history-section">
            <p class="eyebrow" style="margin-bottom: 8px;">Consultas</p>
            <div class="history-list">
              <div v-for="consult in selectedPetConsultations" :key="consult.id" class="history-item">
                <div class="history-item-header">
                  <strong class="history-item-title">{{ formatDate(consult.date) }}</strong>
                  <span class="chip chip--sage" style="font-size: 0.75rem;">{{ consult.diagnosis || 'Sin diagnóstico' }}</span>
                </div>
                <p class="history-item-desc">{{ consult.symptoms || consult.notes || 'Consulta de rutina' }}</p>
              </div>
            </div>
          </div>
          
          <div v-if="selectedPetVaccines.length > 0" class="history-section">
            <p class="eyebrow" style="margin-bottom: 8px;">Vacunas</p>
            <div class="history-list">
              <div v-for="vaccine in selectedPetVaccines" :key="vaccine.id" class="history-item">
                <div class="history-item-header">
                  <strong class="history-item-title">{{ vaccine.name }}</strong>
                  <span class="history-item-date">{{ formatDate(vaccine.date) }}</span>
                </div>
                <p v-if="vaccine.nextDate" class="history-item-next">Próxima dosis: {{ formatDate(vaccine.nextDate) }}</p>
              </div>
            </div>
          </div>

          <div v-if="selectedPetDewormings.length > 0" class="history-section">
            <p class="eyebrow" style="margin-bottom: 8px;">Desparasitaciones</p>
            <div class="history-list">
              <div v-for="deworm in selectedPetDewormings" :key="deworm.id" class="history-item">
                <div class="history-item-header">
                  <strong class="history-item-title">{{ deworm.product }}</strong>
                  <span class="history-item-date">{{ formatDate(deworm.date) }}</span>
                </div>
                <p v-if="deworm.nextDate" class="history-item-next">Próxima dosis: {{ formatDate(deworm.nextDate) }}</p>
              </div>
            </div>
          </div>
          
          <div v-if="selectedPetConsultations.length === 0 && selectedPetVaccines.length === 0 && selectedPetDewormings.length === 0">
            <p class="muted">No hay registros médicos disponibles para esta mascota.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.header-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pet-header-info {
  display: flex; 
  gap: 20px; 
  align-items: center; 
  padding-bottom: 20px; 
  border-bottom: 1px solid rgba(194, 167, 105, 0.15);
}

.pet-name {
  margin: 0; 
  font-size: 1.6rem; 
  color: var(--text-strong);
}

.pet-summary {
  margin: 4px 0 0; 
  color: rgba(61, 61, 61, 0.8); 
  font-size: 1rem;
}

.pet-data {
  margin: 4px 0 0; 
  font-weight: 600;
}

.pet-notes {
  margin: 8px 0 0; 
  padding: 12px; 
  background: rgba(194, 167, 105, 0.08); 
  border-radius: 12px; 
  line-height: 1.5;
}

.history-title {
  margin: 24px 0 16px; 
  font-size: 1.2rem; 
  color: var(--text-strong); 
  border-bottom: 1px solid rgba(194, 167, 105, 0.15); 
  padding-bottom: 8px;
}

.history-section {
  margin-bottom: 16px;
}

.history-list {
  display: flex; 
  flex-direction: column; 
  gap: 8px;
}

.history-item {
  padding: 12px; 
  background: var(--surface); 
  border: 1px solid var(--border); 
  border-radius: 8px;
}

.history-item-header {
  display: flex; 
  justify-content: space-between; 
  margin-bottom: 4px;
}

.history-item-title {
  color: var(--text-strong);
}

.history-item-date {
  font-size: 0.85rem; 
  color: var(--text-muted, rgba(61, 61, 61, 0.68));
}

.history-item-desc {
  margin: 0; 
  font-size: 0.9rem; 
  color: var(--text-muted, rgba(61, 61, 61, 0.68));
}

.history-item-next {
  margin: 0; 
  font-size: 0.85rem; 
  color: var(--text-muted, rgba(61, 61, 61, 0.68));
}
</style>
