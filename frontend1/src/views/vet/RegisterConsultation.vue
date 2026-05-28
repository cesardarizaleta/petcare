<script setup>
  import { computed, reactive } from 'vue';
  import { useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();

  const todayAppointments = computed(() =>
    appStore.appointments.filter(
      (item) =>
        item.status === 'in_progress' || item.status === 'confirmed' || item.status === 'completed'
    )
  );
  const form = reactive({
    appointmentId: todayAppointments.value[0]?.id || '',
    weight: '',
    temperature: '',
    symptoms: '',
    diagnosis: '',
    treatment: '',
    prescriptions: '',
    followUpDate: '',
    notes: '',
  });

  function saveConsultation() {
    const appointment = appStore.appointments.find((item) => item.id === form.appointmentId);
    if (!appointment || !form.diagnosis || !form.treatment) {
      toastStore.push({ title: 'Completa la consulta', type: 'error' });
      return;
    }

    appStore.addConsultation({
      id: `c${Date.now()}`,
      appointmentId: appointment.id,
      petId: appointment.petId,
      vetId: appointment.vetId,
      date: appointment.date,
      weight: Number(form.weight) || 0,
      temperature: Number(form.temperature) || 0,
      symptoms: form.symptoms,
      diagnosis: form.diagnosis,
      treatment: form.treatment,
      prescriptions: form.prescriptions.split('\n').filter(Boolean),
      followUpDate: form.followUpDate || undefined,
      notes: form.notes,
    });

    appStore.updateAppointment({ ...appointment, status: 'completed' });
    toastStore.push({
      title: 'Consulta guardada',
      description: 'La historia clínica quedó actualizada.',
      type: 'success',
    });
    router.push('/vet/records');
  }
</script>

<template>
  <div class="stack">
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
              v-for="appointment in todayAppointments"
              :key="appointment.id"
              :value="appointment.id"
            >
              {{ appointment.date }} · {{ appointment.time }} ·
              {{ appStore.pets.find((pet) => pet.id === appointment.petId)?.name }}
            </option>
          </select>
        </label>

        <div class="input-grid">
          <label class="field"
            ><span>Peso</span
            ><input v-model="form.weight" class="input" type="number" min="0" step="0.1"
          /></label>
          <label class="field"
            ><span>Temperatura</span
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
        <button class="btn btn--primary" type="button" @click="saveConsultation">
          Guardar consulta
        </button>
      </div>
    </section>
  </div>
</template>
