<script setup>
  import { reactive, ref, onMounted, computed } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { useConfirmStore } from '@/stores/useConfirmStore';
  import { formatDate, todayISO } from '@/lib/petcare';
  import http from '@/lib/http';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const confirmStore = useConfirmStore();
  const loading = ref(false);
  const vaccineHistory = ref([]);
  const selectedSupplyId = ref('');

  const form = reactive({
    petId: '',
    date: todayISO(),
    nextDate: '',
    dose: '',
    notes: '',
  });

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchAppointmentsToday(),
        appStore.fetchPets(),
        appStore.fetchInventory()
      ]);
    } catch (err) {
      console.error(err);
    }
  });

  const vaccineSupplies = computed(() => {
    return appStore.inventory.filter(item => item.category === 'VACCINE');
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
    if (!form.petId || !selectedSupplyId.value || !form.date) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
      return;
    }

    const supply = appStore.inventory.find(s => s.id === selectedSupplyId.value);
    if (!supply) {
      toastStore.push({ title: 'Insumo no encontrado', type: 'error' });
      return;
    }

    if (supply.quantity < 1) {
      toastStore.push({
        title: 'Stock insuficiente',
        description: `No hay unidades disponibles de ${supply.name} en el inventario para aplicar.`,
        type: 'error'
      });
      return;
    }

    if (form.dose) {
      const cleanDose = form.dose.trim();
      if (/-\d/.test(cleanDose) || cleanDose.startsWith('-')) {
        toastStore.push({ title: 'Error de validación', description: 'La dosis no puede ser negativa.', type: 'error' });
        return;
      }
    }

    const todayStr = todayISO();
    if (form.date > todayStr) {
      toastStore.push({
        title: 'Fecha inválida',
        description: 'La fecha de aplicación no puede ser una fecha futura.',
        type: 'error',
      });
      return;
    }

    if (form.nextDate && form.nextDate <= form.date) {
      toastStore.push({
        title: 'Fecha inválida',
        description: 'La próxima fecha debe ser posterior a la fecha de aplicación.',
        type: 'error',
      });
      return;
    }

    const selectedPet = appStore.pets.find(p => p.id === form.petId);
    const petName = selectedPet ? selectedPet.name : 'el paciente';
    const autoBatch = supply.batches[0]?.batch || 'AUTO';

    const isConfirmed = await confirmStore.confirm({
      title: 'Registrar Vacuna',
      message: `¿Estás seguro de que deseas registrar la vacuna ${supply.name} para ${petName}? Se descontará 1 unidad del stock de inventario.`,
      confirmText: 'Registrar y Descontar',
      cancelText: 'Cancelar',
      type: 'info',
    });

    if (!isConfirmed) return;

    loading.value = true;
    try {
      // 1. Guardar el registro de vacunación en el historial médico
      await appStore.registerVaccinationEvent(form.petId, {
        vaccine_name: supply.name,
        dose: form.dose || '1 dosis',
        applied_date: form.date,
        next_due_date: form.nextDate || null,
        sanitary_batch: autoBatch,
        event_type: 'VACCINE',
      });

      // 2. Consumir de inventario
      await http.post('/api/v1/inventory/consume/', {
        supply_id: supply.id,
        quantity: 1
      });

      // 3. Recargar inventario local para reflejar el descuento
      await appStore.fetchInventory();

      toastStore.push({
        title: 'Vacuna registrada y descontada',
        description: `Se registró la aplicación de ${supply.name} y se descontó 1 unidad del stock.`,
        type: 'success',
      });

      // Reload history
      await loadVaccineHistory();

      // Reset form selection
      selectedSupplyId.value = '';
      form.dose = '';
      form.notes = '';
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.error || 'Error al registrar vacuna y descontar stock.';
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
            <select v-model="form.petId" class="select" @change="loadVaccineHistory">
              <option value="" disabled>Seleccione un paciente...</option>
              <option v-for="pet in appStore.pets" :key="pet.id" :value="pet.id">
                {{ pet.name }} · {{ pet.breed }} ({{ pet.species === 'dog' ? 'Perro' : pet.species === 'cat' ? 'Gato' : pet.species }} - {{ pet.color }})
              </option>
            </select>
          </label>
          
          <div class="input-grid">
            <label class="field">
              <span>Seleccionar Vacuna *</span>
              <select v-model="selectedSupplyId" class="select">
                <option value="" disabled>Seleccione una vacuna...</option>
                <option v-for="item in vaccineSupplies" :key="item.id" :value="item.id" :disabled="item.quantity < 1">
                  {{ item.name }} (Stock: {{ item.quantity }} uds.)
                </option>
              </select>
            </label>
            <label class="field">
              <span>Dosis</span>
              <input v-model="form.dose" class="input" type="text" placeholder="1 dosis" />
            </label>
          </div>

          <div class="input-grid">
            <label class="field">
              <span>Fecha de aplicación *</span>
              <input v-model="form.date" class="input" type="date" />
            </label>
            <label class="field">
              <span>Próxima fecha</span>
              <input v-model="form.nextDate" class="input" type="date" />
            </label>
          </div>

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

<style scoped>
  .select,
  .input,
  .textarea {
    max-width: 100%;
    min-width: 0;
  }

  .stack > * {
    min-width: 0;
  }

  .split > * {
    min-width: 0;
  }

  @media (max-width: 480px) {
    .card {
      padding: 16px !important;
    }
  }
</style>
