<script setup>
  import { reactive, ref, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { formatDate, todayISO } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const loading = ref(false);
  const vaccineHistory = ref([]);
  const selectedPetId = ref('');

  const form = reactive({
    petId: '',
    name: '',
    date: todayISO(),
    nextDate: '',
    lot: '',
    dose: '',
    notes: '',
  });

  onMounted(async () => {
    // Load pets for the vet to see
    // Pets might be populated from today's appointments
    await appStore.fetchAppointmentsToday();
    await appStore.fetchPets();
  });

  async function loadVaccineHistory() {
    if (!form.petId) return;
    try {
      const data = await appStore.fetchVaccinationSchedule(form.petId);
      vaccineHistory.value = data;
    } catch (e) {
      console.error('Error loading vaccine history:', e);
    }
  }

  async function saveVaccine() {
    if (!form.petId || !form.name || !form.date) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
      return;
    }

    loading.value = true;
    try {
      await appStore.registerVaccinationEvent(form.petId, {
        vaccine_name: form.name,
        dose: form.dose || '1 dosis',
        applied_date: form.date,
        next_due_date: form.nextDate || null,
        sanitary_batch: form.lot,
        event_type: 'VACCINE',
      });

      toastStore.push({
        title: 'Vacuna registrada',
        description: 'El registro de vacunación fue guardado en la base de datos.',
        type: 'success',
      });

      // Reload history
      await loadVaccineHistory();

      // Reset form
      form.name = '';
      form.lot = '';
      form.dose = '';
      form.notes = '';
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.error || 'Error al registrar vacuna.';
      toastStore.push({ title: 'Error', description: detail, type: 'error' });
    } finally {
      loading.value = false;
    }
  }
</script>

<template>
  <div class="stack">
    <PageHeader title="Vacunas" subtitle="Gestión y programación de vacunas por mascota." />

    <section class="split">
      <section class="card">
        <div class="input-row">
          <label class="field">
            <span>Seleccionar Paciente (mascota) *</span>
            <div class="input-grid">
              <select v-model="form.petId" class="select" @change="loadVaccineHistory">
                <option value="" disabled>Seleccione un paciente...</option>
                <option v-for="pet in appStore.pets" :key="pet.id" :value="pet.id">
                  {{ pet.name }} · {{ pet.breed }} ({{ pet.species === 'dog' ? 'Perro' : pet.species === 'cat' ? 'Gato' : pet.species }})
                </option>
              </select>
              <button class="btn btn--soft" type="button" @click="loadVaccineHistory">
                Cargar historial
              </button>
            </div>
          </label>
          <div class="input-grid">
            <label class="field"
              ><span>Vacuna *</span
              ><input v-model="form.name" class="input" type="text" placeholder="Séxtuple"
            /></label>
            <label class="field"
              ><span>Lote</span><input v-model="form.lot" class="input" type="text"
            /></label>
          </div>
          <div class="input-grid">
            <label class="field"
              ><span>Dosis</span><input v-model="form.dose" class="input" type="text" placeholder="1 dosis"
            /></label>
            <label class="field"
              ><span>Fecha *</span><input v-model="form.date" class="input" type="date"
            /></label>
          </div>
          <label class="field">
            <span>Próxima fecha</span><input v-model="form.nextDate" class="input" type="date" />
          </label>
          <button class="btn btn--primary" type="button" :disabled="loading" @click="saveVaccine">
            {{ loading ? 'Guardando...' : 'Guardar vacuna' }}
          </button>
        </div>
      </section>

      <section class="card table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Vacuna</th>
              <th>Fecha</th>
              <th>Próxima</th>
              <th>Lote</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in vaccineHistory" :key="item.id" class="table__row">
              <td>{{ item.vaccine_name || item.event_type }}</td>
              <td>{{ formatDate(item.applied_date) }}</td>
              <td>{{ item.next_due_date ? formatDate(item.next_due_date) : '—' }}</td>
              <td>{{ item.lot || item.sanitary_batch || '—' }}</td>
            </tr>
            <tr v-if="!vaccineHistory.length">
              <td colspan="4" class="muted">Ingrese un ID de paciente y cargue el historial.</td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </div>
</template>
