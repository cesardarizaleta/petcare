<script setup>
  import { computed, reactive, ref, onMounted, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { getOwnerPets, timeSlots, todayISO } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();
  const step = ref(1);

  const freeSlots = ref([]);
  const loadingSlots = ref(false);

  onMounted(async () => {
    try {
      loadingSlots.value = true;
      const slotsData = await appStore.fetchVetSlots(1);
      freeSlots.value = slotsData;
      await Promise.all([
        appStore.fetchProfile(),
        appStore.fetchPets(),
      ]);
    } catch (err) {
      console.error('Error fetching owner data in schedule appointment:', err);
    } finally {
      loadingSlots.value = false;
    }
  });

  const pets = computed(() => getOwnerPets(appStore.pets, appStore.currentUserId));

  const getLocalDateStr = (d = new Date()) => {
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  };

  const todayStr = ref(getLocalDateStr());
  
  const getMaxDateStr = () => {
    const d = new Date();
    d.setMonth(d.getMonth() + 6);
    return getLocalDateStr(d);
  };
  const maxDateStr = ref(getMaxDateStr());

  const form = reactive({
    petId: '',
    date: todayStr.value,
    time: '09:00',
    reason: '',
    notes: '',
  });

  const availableHours = computed(() => {
    if (!form.date) return [];
    let dateSlots = freeSlots.value.filter(s => s.date === form.date && s.status === 'FREE');
    
    if (form.date === todayStr.value) {
      const now = new Date();
      const currentHour = String(now.getHours()).padStart(2, '0');
      const currentMin = String(now.getMinutes()).padStart(2, '0');
      const currentHourStr = `${currentHour}:${currentMin}`;
      dateSlots = dateSlots.filter(s => {
        const slotTime = s.start_time.slice(0, 5); // "HH:MM"
        return slotTime > currentHourStr;
      });
    }

    return dateSlots.map(s => s.start_time.slice(0, 5)).sort();
  });

  watch(
    availableHours,
    (hours) => {
      if (hours.length > 0 && !hours.includes(form.time)) {
        form.time = hours[0];
      } else if (hours.length === 0) {
        form.time = '';
      }
    },
    { immediate: true }
  );

  watch(
    pets,
    (newPets) => {
      if (newPets.length && !form.petId) {
        form.petId = newPets[0].id;
      }
    },
    { immediate: true, deep: true }
  );

  function nextStep() {
    step.value = Math.min(step.value + 1, 3);
  }

  function previousStep() {
    step.value = Math.max(step.value - 1, 1);
  }

  const loading = ref(false);

  async function scheduleAppointment() {
    if (!form.petId || !form.reason) {
      toastStore.push({ title: 'Completa la información requerida', type: 'error' });
      return;
    }

    loading.value = true;
    try {
      await appStore.addAppointment({
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
      router.push('/portal/appointments');
    } catch (err) {
      console.error(err);
      toastStore.push({ title: 'Error', description: 'No se pudo registrar la cita.', type: 'error' });
    } finally {
      loading.value = false;
    }
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

      <div v-else-if="step === 2" class="input-grid" style="margin-top: 18px">
        <label class="field">
          <span>Fecha</span>
          <input v-model="form.date" class="input" type="date" :min="todayStr" :max="maxDateStr" />
        </label>
        <label class="field">
          <span>Hora</span>
          <select v-model="form.time" class="select" :disabled="availableHours.length === 0">
            <option v-if="availableHours.length === 0" value="">No hay horarios disponibles</option>
            <option v-for="hour in availableHours" :key="hour" :value="hour">{{ hour }}</option>
          </select>
        </label>
      </div>

      <div v-else class="input-row" style="margin-top: 18px">
        <label class="field">
          <span>Motivo</span>
          <input v-model="form.reason" class="input" type="text" placeholder="Control anual" />
        </label>
        <label class="field">
          <span>Notas</span>
          <textarea
            v-model="form.notes"
            class="textarea"
            rows="4"
            placeholder="Detalles adicionales"
          />
        </label>
      </div>

      <div class="toolbar" style="margin-top: 20px">
        <button class="btn btn--ghost" type="button" :disabled="step === 1" @click="previousStep">
          Atrás
        </button>
        <div class="toolbar__group">
          <button v-if="step < 3" class="btn btn--primary" type="button" @click="nextStep">
            Continuar
          </button>
          <button v-else class="btn btn--primary" type="button" :disabled="loading" @click="scheduleAppointment">
            {{ loading ? 'Agendando...' : 'Confirmar cita' }}
          </button>

        </div>
      </div>
    </section>
  </div>
</template>
