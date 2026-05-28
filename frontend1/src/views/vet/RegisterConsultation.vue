<script setup>
  import { computed, reactive, ref, onMounted, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();

  const mode = ref('direct'); // Default to direct consultation so they are never blocked

  const todayAppointments = computed(() =>
    appStore.appointments.filter(
      (item) =>
        item.status === 'in_progress' || item.status === 'confirmed' || item.status === 'completed'
    )
  );

  const form = reactive({
    appointmentId: '',
    petId: '',
    weight: '',
    temperature: '',
    symptoms: '',
    diagnosis: '',
    treatment: '',
    prescriptions: '',
    followUpDate: '',
    notes: '',
  });

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchPets(),
        appStore.fetchAppointments()
      ]);
    } catch (err) {
      console.error('Error fetching register consultation form data:', err);
    }
  });

  watch(
    todayAppointments,
    (appt) => {
      if (appt.length && !form.appointmentId) {
        form.appointmentId = appt[0].id;
      }
    },
    { immediate: true }
  );

  watch(
    () => appStore.pets,
    (pets) => {
      if (pets.length && !form.petId) {
        form.petId = pets[0].id;
      }
    },
    { immediate: true, deep: true }
  );

  async function saveConsultation() {
    let appointmentId = form.appointmentId;
    let selectedPetId = form.petId;
    let vetId = 'v1';

    if (mode.value === 'direct') {
      if (!form.petId) {
        toastStore.push({ title: 'Selecciona una mascota', type: 'error' });
        return;
      }
      if (!form.diagnosis || !form.treatment) {
        toastStore.push({ title: 'Completa el diagnóstico y tratamiento', type: 'error' });
        return;
      }

      // Auto-crear cita/turno de consulta directa
      try {
        const todayStr = new Date().toISOString().split('T')[0];
        const timeStr = new Date().toTimeString().slice(0, 5);

        const newAppt = await appStore.addAppointment({
          petId: form.petId,
          date: todayStr,
          time: timeStr,
          reason: 'Consulta médica directa (Walk-in)',
          notes: form.notes,
        });

        appointmentId = newAppt.id;
        selectedPetId = newAppt.petId;
        vetId = newAppt.vetId;
      } catch (err) {
        console.error('Error auto-creating walk-in appointment:', err);
        toastStore.push({
          title: 'Error de Turno',
          description: 'No se pudo crear la cita automática. Asegúrate de tener mascotas registradas.',
          type: 'error',
        });
        return;
      }
    } else {
      const appointment = appStore.appointments.find((item) => item.id === form.appointmentId);
      if (!appointment) {
        toastStore.push({ title: 'Selecciona una cita válida', type: 'error' });
        return;
      }
      if (!form.diagnosis || !form.treatment) {
        toastStore.push({ title: 'Completa el diagnóstico y tratamiento', type: 'error' });
        return;
      }
      appointmentId = appointment.id;
      selectedPetId = appointment.petId;
      vetId = appointment.vetId;
    }

    try {
      await appStore.addConsultation({
        appointmentId: appointmentId,
        petId: selectedPetId,
        vetId: vetId,
        diagnosis: form.diagnosis,
        treatment: form.treatment,
        symptoms: form.symptoms,
        weight: Number(form.weight) || 0,
        temperature: Number(form.temperature) || 0,
        prescriptions: form.prescriptions.split('\n').filter(Boolean),
        followUpDate: form.followUpDate || undefined,
        notes: form.notes,
      });

      toastStore.push({
        title: 'Consulta guardada',
        description: 'La historia clínica quedó actualizada en el servidor.',
        type: 'success',
      });
      router.push('/vet/records');
    } catch (err) {
      console.error('Error saving consultation:', err);
      toastStore.push({
        title: 'Error de Red',
        description: 'No se pudo registrar la consulta médica.',
        type: 'error',
      });
    }
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
        <!-- Modo de Consulta -->
        <label class="field">
          <span>Modo de Registro</span>
          <select v-model="mode" class="select">
            <option value="direct">Consulta Directa (Sin cita previa - Walk-in)</option>
            <option value="scheduled">Cita Programada hoy</option>
          </select>
        </label>

        <!-- Turno Programado -->
        <label class="field" v-if="mode === 'scheduled'">
          <span>Selecciona la Cita</span>
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
          <p v-if="!todayAppointments.length" class="muted" style="margin-top: 6px; font-size: 0.82rem; color: var(--color-danger-dark);">
            No hay citas programadas hoy. Usa el modo de "Consulta Directa".
          </p>
        </label>

        <!-- Mascota para Consulta Directa -->
        <label class="field" v-if="mode === 'direct'">
          <span>Selecciona la Mascota</span>
          <select v-model="form.petId" class="select">
            <option v-for="pet in appStore.pets" :key="pet.id" :value="pet.id">
              {{ pet.name }} ({{ pet.species === 'dog' ? 'Perro' : pet.species === 'cat' ? 'Gato' : pet.species === 'bird' ? 'Ave' : pet.species === 'rabbit' ? 'Conejo' : 'Otro' }} · {{ pet.breed }})
            </option>
          </select>
        </label>

        <div class="input-grid">
          <label class="field"
            ><span>Peso (kg)</span
            ><input v-model="form.weight" class="input" type="number" min="0" step="0.1" placeholder="Ej. 12.5"
          /></label>
          <label class="field"
            ><span>Temperatura (°C)</span
            ><input v-model="form.temperature" class="input" type="number" min="0" step="0.1" placeholder="Ej. 38.5"
          /></label>
        </div>

        <label class="field"
          ><span>Síntomas</span><textarea v-model="form.symptoms" class="textarea" rows="3" placeholder="Ej. Pérdida de apetito, letargo" />
        </label>
        <label class="field"
          ><span>Diagnóstico *</span><textarea v-model="form.diagnosis" class="textarea" rows="3" placeholder="Ej. Gastroenteritis leve" />
        </label>
        <label class="field"
          ><span>Tratamiento *</span><textarea v-model="form.treatment" class="textarea" rows="3" placeholder="Ej. Dieta blanda e hidratación" />
        </label>
        <label class="field"
          ><span>Prescripciones</span><textarea
            v-model="form.prescriptions"
            class="textarea"
            rows="3"
            placeholder="Una prescripción por línea"
          />
        </label>
        <div class="input-grid">
          <label class="field"
            ><span>Fecha de Seguimiento</span><input v-model="form.followUpDate" class="input" type="date"
          /></label>
          <label class="field"
            ><span>Notas del Veterinario</span><input v-model="form.notes" class="input" type="text" placeholder="Notas adicionales de control"
          /></label>
        </div>
        <button class="btn btn--primary" type="button" @click="saveConsultation">
          Guardar consulta
        </button>
      </div>
    </section>
  </div>
</template>
