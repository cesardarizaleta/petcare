<script setup>
  import { computed, ref, reactive, onMounted, watch } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import Modal from '@/components/shared/Modal.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { formatDate, getOwnerAppointments, getPet, getVet, getOwnerPets, timeSlots, getTodayShortDate } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const activeFilter = ref('all');

  const freeSlots = ref([]);
  const loadingSlots = ref(false);

  onMounted(async () => {
    try {
      loadingSlots.value = true;
      freeSlots.value = await appStore.fetchVetSlots(1);
      await appStore.fetchPets();
      await appStore.fetchAppointments();
    } catch (err) {
      console.error('Error fetching appointments:', err);
    } finally {
      loadingSlots.value = false;
    }
  });
  
  // Schedule Modal
  const showNewAppointmentModal = ref(false);
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
    { immediate: true }
  );

  async function scheduleAppointment() {
    if (!form.petId || !form.reason || !form.date) {
      toastStore.push({ title: 'Completa la información requerida', type: 'error' });
      return;
    }
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
        notes: '',
      });
      toastStore.push({
        title: 'Cita agendada',
        description: 'La solicitud quedó registrada en el sistema.',
        type: 'success',
      });
      showNewAppointmentModal.value = false;
      form.reason = '';
      form.date = todayStr.value;
      // Reload slots
      freeSlots.value = await appStore.fetchVetSlots(1);
    } catch (err) {
      console.error(err);
      toastStore.push({ title: 'Error', description: err.message || 'No se pudo registrar la cita.', type: 'error' });
    }
  }

  // Cancel Modal
  const isCancelModalOpen = ref(false);
  const selectedAppointment = ref(null);
  const cancelReasonInput = ref('');

  const filteredAppointments = computed(() => {
    const appointments = getOwnerAppointments(appStore.appointments, appStore.currentUserId);

    if (activeFilter.value === 'all') return appointments;
    if (activeFilter.value === 'upcoming')
      return appointments.filter(
        (item) =>
          item.status === 'scheduled' || item.status === 'confirmed' || item.status === 'waiting'
      );
    return appointments.filter((item) => item.status === activeFilter.value);
  });

  function openCancelModal(appointment) {
    selectedAppointment.value = appointment;
    cancelReasonInput.value = '';
    isCancelModalOpen.value = true;
  }

  function closeCancelModal() {
    isCancelModalOpen.value = false;
    selectedAppointment.value = null;
    cancelReasonInput.value = '';
  }

  function canCancel(appointment) {
    if (['completed', 'cancelled', 'checked_in'].includes(appointment.status.toLowerCase())) {
      return false;
    }
    const apptDateTime = new Date(`${appointment.date}T${appointment.time}`);
    const now = new Date();
    return apptDateTime > now;
  }

  async function confirmCancellation() {
    if (!selectedAppointment.value || !cancelReasonInput.value.trim()) return;

    try {
      await appStore.cancelAppointment(selectedAppointment.value.id, cancelReasonInput.value.trim());
      toastStore.push({
        title: 'Cita cancelada',
        description: `${selectedAppointment.value.reason} fue cancelada.`,
        type: 'info',
      });
      closeCancelModal();
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.error || 'No se pudo cancelar la cita.';
      toastStore.push({
        title: 'Error al cancelar',
        description: detail,
        type: 'error',
      });
    }
  }
</script>

<template>
  <div class="stack">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <PageHeader
        title="Mis Citas"
        subtitle="Listado de citas del propietario con filtros por estado y acciones rápidas."
      />
      <button class="btn btn--primary" @click="showNewAppointmentModal = true">+ Nueva Cita</button>
    </div>

    <div class="toolbar" style="display: flex; justify-content: space-between;">
      <div class="toolbar__group">
        <button
          class="btn btn--ghost"
          :class="{ 'btn--primary': activeFilter === 'all' }"
          @click="activeFilter = 'all'"
        >
          Todas
        </button>
        <button
          class="btn btn--ghost"
          :class="{ 'btn--primary': activeFilter === 'upcoming' }"
          @click="activeFilter = 'upcoming'"
        >
          Próximas
        </button>
        <button
          class="btn btn--ghost"
          :class="{ 'btn--primary': activeFilter === 'completed' }"
          @click="activeFilter = 'completed'"
        >
          Completadas
        </button>
        <button
          class="btn btn--ghost"
          :class="{ 'btn--primary': activeFilter === 'cancelled' }"
          @click="activeFilter = 'cancelled'"
        >
          Canceladas
        </button>
      </div>
    </div>

    <section class="card table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Mascota</th>
            <th>Motivo</th>
            <th>Veterinario</th>
            <th>Estado</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr v-for="appointment in filteredAppointments" :key="appointment.id" class="table__row">
            <td>{{ formatDate(appointment.date) }} · {{ appointment.time }}</td>
            <td>{{ getPet(appStore.pets, appointment.petId)?.name }}</td>
            <td>{{ appointment.reason }}</td>
            <td>{{ getVet(appStore.vets, appointment.vetId)?.name }}</td>
            <td><StatusBadge :status="appointment.status" /></td>
            <td>
              <button
                v-if="canCancel(appointment)"
                class="btn btn--soft btn--sm"
                type="button"
                @click="openCancelModal(appointment)"
              >
                Cancelar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Modal de Agendamiento -->
    <Modal
      :isOpen="showNewAppointmentModal"
      title="Agendar Cita"
      @close="showNewAppointmentModal = false"
    >
      <div class="stack">
        <div class="input-row" style="margin-top: 1rem;">
          <label class="field">
            <span>Selecciona la mascota</span>
            <select v-model="form.petId" class="select">
              <option v-for="pet in pets" :key="pet.id" :value="pet.id">
                {{ pet.name }}
              </option>
            </select>
          </label>
          <div class="input-grid">
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
          <label class="field">
            <span>Motivo</span>
            <input v-model="form.reason" class="input" type="text" placeholder="Control anual" />
          </label>
          
          <div class="toolbar" style="margin-top: 20px; justify-content: flex-end; gap: 8px;">
            <button class="btn btn--ghost" type="button" @click="showNewAppointmentModal = false">Cancelar</button>
            <button class="btn btn--primary" type="button" @click="scheduleAppointment">Confirmar</button>
          </div>
        </div>
      </div>
    </Modal>

    <!-- Modal de Cancelación Personalizado -->
    <Modal
      :isOpen="isCancelModalOpen"
      title="Cancelar Cita"
      @close="closeCancelModal"
    >
      <div class="stack">
        <p class="modal-desc">
          Por favor, indica el motivo de la cancelación para la cita de 
          <strong>{{ getPet(appStore.pets, selectedAppointment?.petId)?.name }}</strong>.
        </p>
        
        <label class="field" style="margin-top: 12px;">
          <span>Motivo de cancelación</span>
          <input
            v-model="cancelReasonInput"
            class="input"
            type="text"
            placeholder="Ej. Cambio de planes, Mascota recuperada"
            @keyup.enter="confirmCancellation"
            style="width: 100%"
          />
        </label>
        
        <div class="toolbar" style="margin-top: 20px; justify-content: flex-end; gap: 8px;">
          <button class="btn btn--ghost" type="button" @click="closeCancelModal">Volver</button>
          <button
            class="btn btn--primary"
            type="button"
            :disabled="!cancelReasonInput.trim()"
            @click="confirmCancellation"
          >
            Confirmar Cancelación
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<style scoped>
.modal-desc {
  color: rgba(61, 61, 61, 0.78);
  font-size: 0.92rem;
  line-height: 1.5;
  margin-bottom: 20px;
}
</style>
