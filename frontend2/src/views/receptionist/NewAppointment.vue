<script setup>
  import { computed, reactive, ref, onMounted, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { timeSlots, todayISO } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();
  const loading = ref(false);

  const selectedOwnerId = ref('');

  const form = reactive({
    patientId: '',
    reason: '',
    notes: '',
    date: todayISO(),
    time: '09:00',
  });

  onMounted(async () => {
    loading.value = true;
    try {
      await Promise.all([
        appStore.fetchOwners(),
        appStore.fetchPets(),
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
                {{ pet.name }} · {{ pet.breed }} ({{ pet.species }})
              </option>
            </select>
          </label>
        </div>

        <div class="input-grid">
          <label class="field">
            <span>Motivo de la consulta *</span>
            <input v-model="form.reason" class="input" type="text" placeholder="Control anual / Consulta" required />
          </label>
          <div class="input-grid" style="grid-template-columns: 1fr 1fr; gap: 16px;">
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
