<script setup>
  import { computed, reactive, ref, onMounted, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { formatDate, getOwnerPets, timeSlots, getTodayShortDate } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();
  const step = ref(1);
  
  onMounted(async () => {
    try {
      await appStore.fetchPets();
    } catch (err) {
      console.error('Error loading schedule appointment pets:', err);
    }
  });

  const pets = computed(() => getOwnerPets(appStore.pets, appStore.currentUserId));

  const form = reactive({
    petId: '',
    date: getTodayShortDate(),
    time: '09:00',
    reason: '',
    notes: '',
  });

  watch(
    pets,
    (newPets) => {
      if (newPets.length && !form.petId) {
        form.petId = newPets[0].id;
      }
    },
    { immediate: true }
  );

  const occupiedSlots = computed(() => {
    return appStore.appointments
      .filter((a) => a.date === form.date && ['scheduled', 'confirmed'].includes(a.status))
      .map((a) => a.time);
  });

  function nextStep() {
    step.value = Math.min(step.value + 1, 3);
  }

  function previousStep() {
    step.value = Math.max(step.value - 1, 1);
  }

  function scheduleAppointment() {
    if (!form.petId || !form.reason) {
      toastStore.push({ title: 'Completa la información requerida', type: 'error' });
      return;
    }

    appStore.addAppointment({
      id: `a${Date.now()}`,
      petId: form.petId,
      ownerId: appStore.currentUserId,
      vetId: 'v1',
      date: form.date,
      time: form.time,
      reason: form.reason,
      status: 'scheduled',
      notes: form.notes,
    });

    toastStore.push({
      title: 'Cita agendada',
      description: 'La solicitud quedó registrada en el sistema.',
      type: 'success',
    });
    appStore.addNotification({
      title: 'Cita agendada',
      message: `Cita programada para el ${formatDate(form.date)} a las ${form.time}.`,
      type: 'success',
      date: new Date().toISOString()
    });
    router.push('/portal/appointments');
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Agendar Cita"
      subtitle="Flujo guiado para reservar una nueva cita de mascota."
    />

    <section class="card">
      <div class="toolbar">
        <div class="toolbar__group">
          <span class="chip" :class="step === 1 ? 'chip--brand' : 'chip--cream'">1. Mascota</span>
          <span class="chip" :class="step === 2 ? 'chip--brand' : 'chip--cream'">2. Fecha</span>
          <span class="chip" :class="step === 3 ? 'chip--brand' : 'chip--cream'"
            >3. Confirmación</span
          >
        </div>
      </div>

      <div v-if="step === 1" class="input-row" style="margin-top: 18px">
        <label class="field">
          <span>Selecciona la mascota</span>
          <select v-model="form.petId" class="select">
            <option v-for="pet in pets" :key="pet.id" :value="pet.id">
              {{ pet.name }} · {{ pet.breed }}
            </option>
          </select>
        </label>
      </div>

      <div v-else-if="step === 2" class="stack" style="margin-top: 18px">
        <label class="field">
          <span>Fecha</span>
          <input v-model="form.date" class="input" type="date" />
        </label>
        <div class="field">
          <span>Hora</span>
          <div class="grid grid--3" style="gap: 8px;">
            <button
              v-for="slot in timeSlots"
              :key="slot"
              type="button"
              class="btn"
              :class="{
                'btn--primary': form.time === slot,
                'btn--ghost': form.time !== slot,
                'btn--disabled': occupiedSlots.includes(slot)
              }"
              :disabled="occupiedSlots.includes(slot)"
              @click="form.time = slot"
              style="justify-content: center;"
            >
              {{ slot }}
            </button>
          </div>
        </div>
      </div>

      <div v-else class="stack" style="margin-top: 18px">
        <div class="card" style="background: var(--color-surface-sunken); padding: 16px; border-radius: 8px; margin-bottom: 16px;">
          <h3 style="margin-bottom: 12px; font-size: 16px;">Resumen de la cita</h3>
          <ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; font-size: 14px;">
            <li><strong>Mascota:</strong> {{ pets.find(p => p.id === form.petId)?.name }}</li>
            <li><strong>Fecha:</strong> {{ formatDate(form.date) }}</li>
            <li><strong>Hora:</strong> {{ form.time }}</li>
          </ul>
        </div>
        <div class="input-row">
          <label class="field">
            <span>Motivo Principal</span>
            <input v-model="form.reason" class="input" type="text" placeholder="Ej. Control anual, Vacunación" />
          </label>
          <label class="field">
            <span>Notas Adicionales</span>
            <textarea
              v-model="form.notes"
              class="textarea"
              rows="3"
              placeholder="Detalles adicionales para el veterinario"
            />
          </label>
        </div>
      </div>

      <div class="toolbar" style="margin-top: 20px">
        <button class="btn btn--ghost" type="button" :disabled="step === 1" @click="previousStep">
          Atrás
        </button>
        <div class="toolbar__group">
          <button v-if="step < 3" class="btn btn--primary" type="button" @click="nextStep">
            Continuar
          </button>
          <button v-else class="btn btn--primary" type="button" @click="scheduleAppointment">
            Confirmar cita
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
