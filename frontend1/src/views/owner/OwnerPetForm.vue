<script setup>
  import { reactive, computed, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { getPet } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const route = useRoute();
  const router = useRouter();

  const isEditing = computed(() => !!route.params.id);
  
  const form = reactive({
    name: '',
    species: 'dog',
    breed: 'Golden Retriever',
    sex: 'M',
    birthDate: '',
    weight: '',
    color: '',
    notes: '',
  });

  const breedsBySpecies = {
    dog: ['Golden Retriever', 'Bulldog Francés', 'Pastor Alemán', 'Labrador', 'Mestizo', 'Otro'],
    cat: ['Persa', 'Siamés', 'Mestizo', 'Otro'],
    bird: ['Canario', 'Loro', 'Otro'],
    rabbit: ['Enano', 'Belier', 'Otro'],
    other: ['Otro']
  };

  const availableBreeds = computed(() => breedsBySpecies[form.species] || ['Otro']);

  onMounted(() => {
    if (isEditing.value) {
      const pet = getPet(appStore.pets, route.params.id);
      if (pet) {
        form.name = pet.name || '';
        form.species = pet.species || 'dog';
        form.breed = pet.breed || availableBreeds.value[0];
        form.sex = pet.sex || 'M';
        form.birthDate = pet.birthDate || '';
        form.weight = pet.weight || '';
        form.color = pet.color || '';
        form.notes = pet.notes || '';
      }
    }
  });

  async function savePet() {
    if (!form.name || !form.breed || !form.birthDate) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
      return;
    }

    try {
      if (isEditing.value) {
        appStore.updatePet({
          id: route.params.id,
          ownerId: appStore.currentUserId,
          name: form.name,
          species: form.species,
          breed: form.breed,
          sex: form.sex,
          birthDate: form.birthDate,
          weight: Number(form.weight) || 0,
          color: form.color,
          notes: form.notes,
        });

        toastStore.push({
          title: 'Mascota actualizada',
          description: `Los datos de ${form.name} fueron actualizados localmente.`,
          type: 'success',
        });
      } else {
        await appStore.addPet({
          name: form.name,
          species: form.species,
          breed: form.breed,
          sex: form.sex,
          birthDate: form.birthDate,
          weight: Number(form.weight) || 0,
          color: form.color,
          notes: form.notes,
        });

        toastStore.push({
          title: 'Mascota agregada',
          description: `${form.name} se sumó al perfil en el servidor.`,
          type: 'success',
        });
      }
      
      router.push('/portal/pets');
    } catch (error) {
      console.error(error);
      toastStore.push({
        title: 'Error al guardar mascota',
        description: 'No se pudo guardar la mascota en el servidor.',
        type: 'error',
      });
    }
  }

  function goBack() {
    router.back();
  }
</script>

<template>
  <div class="stack">
    <div class="header-with-actions">
      <PageHeader 
        :title="isEditing ? 'Editar Mascota' : 'Agregar Mascota'" 
        subtitle="Completa los datos de la mascota para su historia clínica." 
      />
      <button class="btn btn--ghost" type="button" @click="goBack">Volver</button>
    </div>

    <section class="card form-container">
      <div class="input-row">
        <label class="field"
          ><span>Nombre *</span><input v-model="form.name" class="input" type="text"
        /></label>
        <div class="input-grid">
          <label class="field"
            ><span>Especie</span
            ><select v-model="form.species" class="select" @change="form.breed = availableBreeds[0]">
              <option value="dog">Perro</option>
              <option value="cat">Gato</option>
              <option value="bird">Ave</option>
              <option value="rabbit">Conejo</option>
              <option value="other">Otro</option>
            </select></label
          >
          <label class="field"
            ><span>Raza *</span
            ><select v-model="form.breed" class="select">
              <option v-for="breed in availableBreeds" :key="breed" :value="breed">{{ breed }}</option>
            </select></label
          >
        </div>
        <div class="input-grid">
          <label class="field"
            ><span>Sexo</span
            ><select v-model="form.sex" class="select">
              <option value="M">Macho (M)</option>
              <option value="F">Hembra (F)</option>
            </select></label
          >
          <label class="field"
            ><span>Fecha de nacimiento *</span
            ><input v-model="form.birthDate" class="input" type="date"
          /></label>
        </div>
        <div class="input-grid">
          <label class="field"
            ><span>Peso (kg)</span
            ><input v-model="form.weight" class="input" type="number" min="0" step="0.1"
          /></label>
          <label class="field"
            ><span>Color</span><input v-model="form.color" class="input" type="text"
          /></label>
        </div>
        <label class="field"
          ><span>Notas</span><textarea v-model="form.notes" class="textarea" rows="3" />
        </label>
        <div class="form-actions">
          <button class="btn btn--ghost" type="button" @click="goBack">
            Cancelar
          </button>
          <button class="btn btn--primary" type="button" @click="savePet">
            {{ isEditing ? 'Guardar cambios' : 'Agregar mascota' }}
          </button>
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
.form-container {
  max-width: 800px;
}
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
