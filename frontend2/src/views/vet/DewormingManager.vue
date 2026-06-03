<script setup>
  import { reactive, ref, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { formatDate, todayISO, extractApiError, getSpeciesLabel } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const loading = ref(false);
  const dewormingHistory = ref([]);

  onMounted(async () => {
    try {
      await appStore.fetchAppointmentsToday();
      await appStore.fetchPets();
    } catch (err) {
      console.error('Error fetching today appointments/pets in DewormingManager:', err);
    }
  });

  const form = reactive({
    petId: '',
    product: '',
    date: todayISO(),
    nextDate: '',
    weight: '',
    notes: '',
  });

  async function loadHistory() {
    if (!form.petId) return;
    try {
      const data = await appStore.fetchVaccinationSchedule(form.petId);
      // Filter only DEWORMING events
      dewormingHistory.value = data.filter(e => e.event_type === 'DEWORMING');
    } catch (e) {
      console.error('Error loading deworming history:', e);
    }
  }

  async function saveDeworming() {
    if (!form.petId || !form.product || !form.date) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
      return;
    }

    if (form.weight !== '' && form.weight !== null && Number(form.weight) < 0) {
      toastStore.push({ title: 'Error de validación', description: 'El peso no puede ser negativo.', type: 'error' });
      return;
    }

    const todayStr = todayISO();
    if (form.date > todayStr) {
      toastStore.push({
        title: 'Fecha inválida',
        description: 'La fecha de aplicación no puede ser una fecha futura.',
        type: 'error',
      });
      return;
    }

    if (form.nextDate && form.nextDate <= form.date) {
      toastStore.push({
        title: 'Fecha inválida',
        description: 'La próxima fecha debe ser posterior a la fecha de aplicación.',
        type: 'error',
      });
      return;
    }

    loading.value = true;
    try {
      await appStore.registerVaccinationEvent(form.petId, {
        vaccine_name: form.product,
        dose: form.weight ? `${form.weight} kg` : '1 dosis',
        applied_date: form.date,
        next_due_date: form.nextDate || null,
        sanitary_batch: form.notes || '',
        event_type: 'DEWORMING',
      });

      toastStore.push({
        title: 'Desparasitación guardada',
        description: 'El registro fue guardado en la base de datos.',
        type: 'success',
      });

      await loadHistory();
      form.product = '';
      form.weight = '';
      form.notes = '';
    } catch (error) {
      console.error(error);
      toastStore.push({ title: 'Error al guardar', description: extractApiError(error), type: 'error' });
    } finally {
      loading.value = false;
    }
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Desparasitaciones"
      subtitle="Registro y seguimiento de desparasitaciones por paciente."
    />

    <section class="split">
      <section class="card">
        <div class="input-row">
          <label class="field">
            <span>Seleccionar Paciente (mascota) *</span>
            <select v-model="form.petId" class="select" @change="loadHistory">
              <option value="" disabled>Seleccione un paciente...</option>
              <option v-for="pet in appStore.pets" :key="pet.id" :value="pet.id">
                {{ pet.name }} · {{ pet.breed }} ({{ getSpeciesLabel(pet.species) }} - {{ pet.color }})
              </option>
            </select>
          </label>
          <label class="field"
            ><span>Producto *</span
            ><input v-model="form.product" class="input" type="text" placeholder="Milbemax"
          /></label>
          <div class="input-grid">
            <label class="field"
              ><span>Fecha *</span><input v-model="form.date" class="input" type="date"
            /></label>
            <label class="field"
              ><span>Próxima fecha</span><input v-model="form.nextDate" class="input" type="date"
            /></label>
          </div>
          <div class="input-grid">
            <label class="field"
              ><span>Peso (kg)</span
              ><input v-model="form.weight" class="input" type="number" min="0" step="0.1"
            /></label>
            <label class="field"
              ><span>Notas</span><input v-model="form.notes" class="input" type="text"
            /></label>
          </div>
          <button class="btn btn--primary" type="button" :disabled="loading" @click="saveDeworming">
            {{ loading ? 'Guardando...' : 'Guardar desparasitación' }}
          </button>
        </div>
      </section>

      <section class="card table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>Fecha</th>
              <th>Próxima</th>
              <th>Dosis</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in dewormingHistory" :key="item.id" class="table__row">
              <td>{{ item.vaccine_name || item.event_type }}</td>
              <td>{{ formatDate(item.applied_date) }}</td>
              <td>{{ item.next_due_date ? formatDate(item.next_due_date) : '—' }}</td>
              <td>{{ item.dose || '—' }}</td>
            </tr>
            <tr v-if="!dewormingHistory.length">
              <td colspan="4" class="muted">Ingrese un ID de paciente y cargue el historial.</td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </div>
</template>

<style scoped>
  .select,
  .input,
  .textarea {
    max-width: 100%;
    min-width: 0;
  }

  .stack > * {
    min-width: 0;
  }

  .split > * {
    min-width: 0;
  }

  @media (max-width: 480px) {
    .card {
      padding: 16px !important;
    }
  }
</style>
