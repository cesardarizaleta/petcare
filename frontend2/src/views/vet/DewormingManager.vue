<script setup>
  import { reactive, ref, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { formatDate, todayISO } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const loading = ref(false);
  const dewormingHistory = ref([]);

  onMounted(async () => {
    try {
      await appStore.fetchAppointmentsToday();
    } catch (err) {
      console.error('Error fetching today appointments in DewormingManager:', err);
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
      toastStore.push({ title: 'Error al guardar', type: 'error' });
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
            <span>ID del Paciente (mascota)</span>
            <div class="input-grid">
              <input v-model="form.petId" class="input" type="number" placeholder="Ej: 1" />
              <button class="btn btn--soft" type="button" @click="loadHistory">
                Cargar historial
              </button>
            </div>
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
