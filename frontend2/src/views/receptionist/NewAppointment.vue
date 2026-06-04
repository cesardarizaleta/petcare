<script setup>
  import { computed, reactive, ref, onMounted, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { todayISO, extractApiError, getSpeciesLabel } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();
  const loading = ref(false);
  const loadingSlots = ref(false);

  const selectedOwnerId = ref('');
  const availableSlots = ref([]);

  const form = reactive({
    patientId: '',
    reason: '',
    notes: '',
    date: todayISO(),
    time: '',
  });

  async function loadSlots() {
    loadingSlots.value = true;
    try {
      const vetId = 1;
      availableSlots.value = await appStore.fetchVetSlots(vetId);
    } catch (err) {
      console.error('Error fetching veterinarian slots:', err);
    } finally {
      loadingSlots.value = false;
    }
  }

  onMounted(async () => {
    loading.value = true;
    try {
      await Promise.all([
        appStore.fetchOwners(),
        appStore.fetchPets(),
        loadSlots(),
      ]);
    } catch (err) {
      console.error('Error fetching receptionist data in NewAppointment:', err);
    } finally {
      loading.value = false;
    }
  });

  watch(
    () => appStore.owners,
    (owners) => {
      if (owners.length && !selectedOwnerId.value) {
        selectedOwnerId.value = owners[0].id;
      }
    },
    { immediate: true, deep: true }
  );

  const filteredPets = computed(() => {
    return appStore.pets.filter(pet => String(pet.ownerId) === String(selectedOwnerId.value));
  });

  watch(
    filteredPets,
    (pets) => {
      if (pets.length) {
        // If current patientId is not in filtered pets, select first
        const exists = pets.some(p => String(p.id) === String(form.patientId));
        if (!exists) {
          form.patientId = pets[0].id;
        }
      } else {
        form.patientId = '';
      }
    },
    { immediate: true, deep: true }
  );

  const minDate = todayISO();
  const maxDate = computed(() => {
    const d = new Date();
    d.setMonth(d.getMonth() + 6);
    return d.toISOString().slice(0, 10);
  });

  const availableTimesForSelectedDate = computed(() => {
    if (!form.date) return [];
    
    // Filtrar slots para la fecha seleccionada
    let dailySlots = availableSlots.value.filter(s => s.date === form.date);
    
    const todayStr = todayISO();
    if (form.date === todayStr) {
      // Filtrar horarios que ya pasaron en el día de hoy
      const now = new Date();
      const currentHHMM = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
      
      dailySlots = dailySlots.filter(s => {
        const timePart = s.start_time.slice(0, 5);
        return timePart > currentHHMM;
      });
    }

    return dailySlots
      .map(s => s.start_time.slice(0, 5))
      .sort();
  });

  watch(
    () => form.date,
    () => {
      form.time = '';
    }
  );

  async function saveAppointment() {
    if (!form.patientId || !form.reason || !form.date || !form.time) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
      return;
    }

    const todayStr = todayISO();
    const maxStr = maxDate.value;

    if (form.date < todayStr) {
      toastStore.push({
        title: 'Fecha inválida',
        description: 'No se pueden programar citas en el pasado.',
        type: 'error',
      });
      return;
    }

    if (form.date > maxStr) {
      toastStore.push({
        title: 'Fecha inválida',
        description: 'La cita no puede programarse con más de 6 meses de anticipación.',
        type: 'error',
      });
      return;
    }

    loading.value = true;
    try {
      await appStore.createAppointment({
        patient_id: Number(form.patientId),
        reason: form.reason,
        date: form.date,
        time: form.time,
      });

      toastStore.push({
        title: 'Cita creada',
        description: 'La cita fue guardada correctamente en la base de datos.',
        type: 'success',
      });
      router.push('/reception/dashboard');
    } catch (error) {
      console.error(error);
      const detail = extractApiError(error, 'Error al crear la cita.');
      toastStore.push({ title: 'Error', description: detail, type: 'error' });
    } finally {
      loading.value = false;
    }
  }
</script>

<template>
  <div class="stack">
    <PageHeader title="Nueva Cita" subtitle="Alta manual de citas para el equipo de recepción." />

    <section class="card">
      <div class="input-row">
        <div class="input-grid">
          <label class="field">
            <span>Seleccionar Propietario *</span>
            <select v-model="selectedOwnerId" class="select" required>
              <option value="" disabled>Seleccione un propietario...</option>
              <option v-for="owner in appStore.owners" :key="owner.id" :value="owner.id">
                {{ owner.name }} ({{ owner.email }})
              </option>
            </select>
          </label>
          <label class="field">
            <span>Seleccionar Mascota (Paciente) *</span>
            <select v-model="form.patientId" class="select" required>
              <option value="" disabled>Seleccione una mascota...</option>
              <option v-for="pet in filteredPets" :key="pet.id" :value="pet.id">
                {{ pet.name }} · {{ pet.breed }} ({{ getSpeciesLabel(pet.species) }} - {{ pet.color }})
              </option>
            </select>
          </label>
        </div>

        <div class="input-grid">
          <label class="field">
            <span>Motivo de la consulta *</span>
            <input v-model="form.reason" class="input" type="text" placeholder="Control anual / Consulta" required />
          </label>
          <div class="date-time-grid">
            <label class="field">
              <span>Fecha *</span>
              <input v-model="form.date" class="input" type="date" :min="minDate" :max="maxDate" required />
            </label>
            <label class="field">
              <span>Hora *</span>
              <select v-model="form.time" class="select" required :disabled="loadingSlots">
                <option v-if="loadingSlots" disabled>Cargando horarios...</option>
                <option v-else-if="!availableTimesForSelectedDate.length" value="" disabled>
                  No hay horarios disponibles
                </option>
                <option v-else value="" disabled>Seleccione un horario...</option>
                <option v-for="slot in availableTimesForSelectedDate" :key="slot" :value="slot">
                  {{ slot }} hs
                </option>
              </select>
            </label>
          </div>
        </div>

        <label class="field">
          <span>Notas</span>
          <textarea v-model="form.notes" class="textarea" rows="4" />
        </label>

        <button class="btn btn--primary" type="button" :disabled="loading" @click="saveAppointment">
          {{ loading ? 'Guardando...' : 'Guardar cita' }}
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
  .date-time-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
  }

  .select,
  .input,
  .textarea {
    max-width: 100%;
  }

  @media (max-width: 600px) {
    .date-time-grid {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 480px) {
    .card {
      padding: 16px;
    }
  }
</style>
