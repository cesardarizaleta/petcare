<script setup>
  import { computed, reactive, ref, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import {
    formatDate,
    getLatestConsultation,
    getLatestDeworming,
    getLatestVaccine,
    getOwnerPets,
    extractApiError,
    todayISO,
    getSpeciesLabel,
  } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const loading = ref(false);

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchProfile(),
        appStore.fetchPets(),
      ]);
    } catch (err) {
      console.error('Error fetching owner pets data:', err);
    }
  });
  const pets = computed(() => getOwnerPets(appStore.pets, appStore.currentUserId));

  const form = reactive({
    name: '',
    species: 'dog',
    breed: '',
    birthDate: '',
    weight: '',
    color: '',
    notes: '',
  });

  async function addPet() {
    if (!form.name || !form.breed || !form.birthDate) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
      return;
    }

    const todayStr = todayISO();
    if (form.birthDate > todayStr) {
      toastStore.push({
        title: 'Fecha de nacimiento inválida',
        description: 'La fecha de nacimiento no puede ser en el futuro.',
        type: 'error',
      });
      return;
    }

    const weightVal = Number(form.weight);
    if (form.weight !== '' && (isNaN(weightVal) || weightVal <= 0 || weightVal > 100)) {
      toastStore.push({
        title: 'Peso inválido',
        description: 'El peso de la mascota debe estar entre 0.1 kg y 100 kg.',
        type: 'error',
      });
      return;
    }

    loading.value = true;
    try {
      await appStore.addPet({
        id: `p${Date.now()}`,
        ownerId: appStore.currentUserId,
        name: form.name,
        species: form.species,
        breed: form.breed,
        birthDate: form.birthDate,
        weight: Number(form.weight) || 0,
        color: form.color,
        notes: form.notes,
      });

      toastStore.push({
        title: 'Mascota agregada',
        description: `${form.name} se sumó al perfil.`,
        type: 'success',
      });
      form.name = '';
      form.breed = '';
      form.birthDate = '';
      form.weight = '';
      form.color = '';
      form.notes = '';
    } catch (err) {
      console.error(err);
      toastStore.push({ title: 'Error', description: extractApiError(err, 'No se pudo registrar la mascota.'), type: 'error' });
    } finally {
      loading.value = false;
    }
  }

  function sanitizeWeight() {
    if (form.weight === '') return;
    const val = Number(form.weight);
    if (val > 100) {
      form.weight = 100;
    } else if (val < 0) {
      form.weight = 0.1;
    }
  }
</script>


<template>
  <div class="stack">
    <PageHeader title="Mis Mascotas" subtitle="Gestión de mascotas vinculadas al propietario." />

    <section class="split">
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
            <div class="stack" style="justify-items: end; gap: 8px">
              <span class="chip chip--sage">{{ getSpeciesLabel(pet.species) }}</span>
              <span class="muted"
                >Vacunas:
                {{ getLatestVaccine(appStore.vaccines, pet.id) ? 'Activas' : 'Sin datos' }}</span
              >
            </div>
          </article>
          <p v-if="!pets.length" class="muted">Todavía no hay mascotas asociadas.</p>
        </div>
      </DashboardCard>

      <section class="card">
        <h2 class="section__title">Agregar mascota</h2>
        <div class="input-row" style="margin-top: 16px">
          <label class="field"
            ><span>Nombre *</span><input v-model="form.name" class="input" type="text"
          /></label>
          <div class="input-grid">
            <label class="field"
              ><span>Especie</span
              ><select v-model="form.species" class="select">
                <option value="dog">Perro</option>
                <option value="cat">Gato</option>
                <option value="bird">Ave</option>
                <option value="rabbit">Conejo</option>
                <option value="other">Otro</option>
              </select></label
            >
            <label class="field"
              ><span>Raza *</span><input v-model="form.breed" class="input" type="text"
            /></label>
          </div>
          <div class="input-grid">
            <label class="field">
              <span>Fecha de nacimiento *</span>
              <input v-model="form.birthDate" class="input" type="date" :max="todayISO()" required />
            </label>
            <label class="field">
              <span>Peso (kg)</span>
              <input v-model="form.weight" class="input" type="number" min="0.1" max="100" step="0.1" placeholder="Ej: 12.5" @input="sanitizeWeight" />
            </label>
          </div>
          <label class="field"
            ><span>Color</span><input v-model="form.color" class="input" type="text"
          /></label>
          <label class="field"
            ><span>Notas</span><textarea v-model="form.notes" class="textarea" rows="4" />
          </label>
          <button class="btn btn--primary" type="button" :disabled="loading" @click="addPet">
            {{ loading ? 'Guardando mascota...' : 'Guardar mascota' }}
          </button>
        </div>
      </section>
    </section>
  </div>
</template>
