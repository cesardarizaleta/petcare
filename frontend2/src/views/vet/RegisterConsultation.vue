<script setup>
  import { computed, reactive, ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { useConfirmStore } from '@/stores/useConfirmStore';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const confirmStore = useConfirmStore();
  const router = useRouter();
  const loading = ref(false);

  onMounted(async () => {
    await appStore.fetchAppointmentsToday();
  });

  const activeAppointments = computed(() =>
    appStore.appointments.filter(
      (item) =>
        item.status === 'in_progress' || item.status === 'confirmed' ||
        item.status === 'checked_in' || item.status === 'completed'
    )
  );

  const form = reactive({
    appointmentId: '',
    weight: '',
    temperature: '',
    symptoms: '',
    diagnosis: '',
    treatment: '',
    prescriptions: '',
    followUpDate: '',
    notes: '',
  });

  // Auto-select first appointment when data loads
  const unwatchAppointments = computed(() => {
    if (activeAppointments.value.length && !form.appointmentId) {
      form.appointmentId = activeAppointments.value[0].id;
    }
    return null;
  });

  async function saveConsultation() {
    if (!form.appointmentId || !form.diagnosis || !form.treatment) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
      return;
    }

    if (form.weight !== '' && form.weight !== null) {
      const wVal = Number(form.weight);
      if (isNaN(wVal) || wVal <= 0) {
        toastStore.push({ title: 'Error de validación', description: 'El peso debe ser mayor a 0 kg.', type: 'error' });
        return;
      }
    }
    if (form.temperature !== '' && form.temperature !== null) {
      const tVal = Number(form.temperature);
      if (isNaN(tVal) || tVal < 30.0 || tVal > 45.0) {
        toastStore.push({ title: 'Error de validación', description: 'La temperatura debe estar en un rango fisiológico real (entre 30°C y 45°C).', type: 'error' });
        return;
      }
    }

    const isConfirmed = await confirmStore.confirm({
      title: 'Guardar Consulta',
      message: '¿Estás seguro de que deseas guardar esta consulta clínica? Se registrarán el diagnóstico y el tratamiento de forma permanente.',
      confirmText: 'Sí, guardar consulta',
      cancelText: 'Cancelar',
      type: 'success',
    });

    if (!isConfirmed) return;

    loading.value = true;
    try {
      await appStore.saveConsultation(form.appointmentId, {
        diagnosis: form.diagnosis,
        treatment: form.treatment,
        symptoms: form.symptoms,
        weight: form.weight !== '' && form.weight !== null ? Number(form.weight) : null,
        temperature: form.temperature !== '' && form.temperature !== null ? Number(form.temperature) : null,
        prescriptions: form.prescriptions,
        notes: form.notes,
        follow_up_date: form.followUpDate || null,
      });

      toastStore.push({
        title: 'Consulta guardada',
        description: 'La historia clínica quedó actualizada en la base de datos.',
        type: 'success',
      });
      router.push('/vet/records');
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.error || 'Error al guardar la consulta.';
      toastStore.push({ title: 'Error', description: detail, type: 'error' });
    } finally {
      loading.value = false;
    }
  }
</script>

<template>
  <div class="stack">
    <!-- Force computed evaluation -->
    <span style="display:none">{{ unwatchAppointments }}</span>

    <PageHeader
      title="Registrar Consulta"
      subtitle="Carga clínica para consultas realizadas en el consultorio."
    />

    <section class="card">
      <div class="input-row">
        <label class="field">
          <span>Turno</span>
          <select v-model="form.appointmentId" class="select">
            <option
              v-for="appointment in activeAppointments"
              :key="appointment.id"
              :value="appointment.id"
            >
              {{ appointment.date }} · {{ appointment.time }} · {{ appointment.petName || 'Paciente' }}
            </option>
          </select>
        </label>

        <div class="input-grid">
          <label class="field"
            ><span>Peso (kg)</span
            ><input v-model="form.weight" class="input" type="number" min="0" step="0.1"
          /></label>
          <label class="field"
            ><span>Temperatura (°C)</span
            ><input v-model="form.temperature" class="input" type="number" min="0" step="0.1"
          /></label>
        </div>

        <label class="field"
          ><span>Síntomas</span><textarea v-model="form.symptoms" class="textarea" rows="3" />
        </label>
        <label class="field"
          ><span>Diagnóstico *</span><textarea v-model="form.diagnosis" class="textarea" rows="3" />
        </label>
        <label class="field"
          ><span>Tratamiento *</span><textarea v-model="form.treatment" class="textarea" rows="3" />
        </label>
        <label class="field"
          ><span>Prescripciones</span
          ><textarea
            v-model="form.prescriptions"
            class="textarea"
            rows="3"
            placeholder="Una por línea"
          />
        </label>
        <div class="input-grid">
          <label class="field"
            ><span>Seguimiento</span><input v-model="form.followUpDate" class="input" type="date"
          /></label>
          <label class="field"
            ><span>Notas</span><input v-model="form.notes" class="input" type="text"
          /></label>
        </div>
        <button class="btn btn--primary" type="button" :disabled="loading" @click="saveConsultation">
          {{ loading ? 'Guardando...' : 'Guardar consulta' }}
        </button>
      </div>
    </section>
  </div>
</template>
