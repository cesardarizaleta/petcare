<script setup>
  import { reactive, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { timeSlots, todayISO } from '@/lib/petcare';
  import http from '@/lib/http';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();
  const loading = ref(false);
  const patients = ref([]);
  const searchQuery = ref('');

  const form = reactive({
    patientId: '',
    reason: '',
    notes: '',
    date: todayISO(),
    time: '09:00',
  });

  async function searchPatients() {
    if (!searchQuery.value || searchQuery.value.length < 2) return;
    try {
      // Search patients by name via the backend
      const res = await http.get('/api/v1/appointments/', { params: { search: searchQuery.value } });
      // Extract unique patients from appointment responses
      // For now, just populate from the appStore's known pets
    } catch (e) {
      console.error(e);
    }
  }

  async function saveAppointment() {
    if (!form.patientId || !form.reason) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
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
      const detail = error.response?.data?.error || 'Error al crear la cita.';
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
            <span>ID del Paciente (mascota)</span>
            <input v-model="form.patientId" class="input" type="number" placeholder="Ej: 1" />
          </label>
          <label class="field">
            <span>Motivo de la consulta *</span>
            <input v-model="form.reason" class="input" type="text" placeholder="Control anual" />
          </label>
        </div>

        <div class="input-grid">
          <label class="field">
            <span>Fecha</span>
            <input v-model="form.date" class="input" type="date" />
          </label>
          <label class="field">
            <span>Hora</span>
            <select v-model="form.time" class="select">
              <option v-for="slot in timeSlots" :key="slot" :value="slot">{{ slot }}</option>
            </select>
          </label>
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
