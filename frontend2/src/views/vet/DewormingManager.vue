<script setup>
  import { reactive, ref, onMounted, computed } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { useConfirmStore } from '@/stores/useConfirmStore';
  import { formatDate, todayISO, extractApiError } from '@/lib/petcare';
  import http from '@/lib/http';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const confirmStore = useConfirmStore();
  const loading = ref(false);
  const dewormingHistory = ref([]);
  const selectedSupplyId = ref('');

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchAppointmentsToday(),
        appStore.fetchPets(),
        appStore.fetchInventory()
      ]);
    } catch (err) {
      console.error('Error fetching today appointments/pets/inventory in DewormingManager:', err);
    }
  });

  const form = reactive({
    petId: '',
    date: todayISO(),
    nextDate: '',
    weight: '',
    notes: '',
  });

  const dewormingSupplies = computed(() => {
    return appStore.inventory.filter(item => item.category === 'MEDICINE');
  });

  async function loadHistory() {
    if (!form.petId) return;
    try {
      const data = await appStore.fetchVaccinationSchedule(form.petId);
      // Filter only DEWORMING events
      dewormingHistory.value = data.filter(e => e.event_type === 'DEWORMING');
    } catch (e) {
      console.error('Error loading deworming history:', e);
    }
  }

  async function saveDeworming() {
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

    if (form.weight !== '' && form.weight !== null && Number(form.weight) < 0) {
      toastStore.push({ title: 'Error de validación', description: 'El peso no puede ser negativo.', type: 'error' });
      return;
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
      title: 'Registrar Desparasitación',
      message: `¿Estás seguro de que deseas registrar la desparasitación con ${supply.name} para ${petName}? Se descontará 1 unidad del stock de inventario.`,
      confirmText: 'Registrar y Descontar',
      cancelText: 'Cancelar',
      type: 'info',
    });

    if (!isConfirmed) return;

    loading.value = true;
    try {
      // 1. Guardar el registro de vacunación/desparasitación
      await appStore.registerVaccinationEvent(form.petId, {
        vaccine_name: supply.name,
        dose: form.weight ? `${form.weight} kg` : '1 dosis',
        applied_date: form.date,
        next_due_date: form.nextDate || null,
        sanitary_batch: autoBatch,
        event_type: 'DEWORMING',
      });

      // 2. Consumir de inventario
      await http.post('/api/v1/inventory/consume/', {
        supply_id: supply.id,
        quantity: 1
      });

      // 3. Recargar inventario para actualizar niveles
      await appStore.fetchInventory();

      toastStore.push({
        title: 'Desparasitación registrada y descontada',
        description: `Se registró la aplicación de ${supply.name} y se descontó 1 unidad del stock.`,
        type: 'success',
      });

      await loadHistory();
      selectedSupplyId.value = '';
      form.weight = '';
      form.notes = '';
    } catch (error) {
      console.error(error);
      toastStore.push({ title: 'Error al guardar', description: extractApiError(error), type: 'error' });
    } finally {
      loading.value = false;
    }
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Desparasitaciones"
      subtitle="Registro y seguimiento de desparasitaciones por paciente."
    />

    <section class="split">
      <section class="card">
        <div class="input-row">
          <label class="field">
            <span>Seleccionar Paciente (mascota) *</span>
            <select v-model="form.petId" class="select" @change="loadHistory">
              <option value="" disabled>Seleccione un paciente...</option>
              <option v-for="pet in appStore.pets" :key="pet.id" :value="pet.id">
                {{ pet.name }} · {{ pet.breed }} ({{ pet.species === 'dog' ? 'Perro' : pet.species === 'cat' ? 'Gato' : pet.species }} - {{ pet.color }})
              </option>
            </select>
          </label>
          
          <div class="input-grid">
            <label class="field">
              <span>Seleccionar Desparasitante *</span>
              <select v-model="selectedSupplyId" class="select">
                <option value="" disabled>Seleccione un producto...</option>
                <option v-for="item in dewormingSupplies" :key="item.id" :value="item.id" :disabled="item.quantity < 1">
                  {{ item.name }} (Stock: {{ item.quantity }} uds.)
                </option>
              </select>
            </label>
            <label class="field">
              <span>Peso (kg)</span>
              <input v-model="form.weight" class="input" type="number" min="0" step="0.1" />
            </label>
          </div>

          <div class="input-grid">
            <label class="field">
              <span>Fecha *</span>
              <input v-model="form.date" class="input" type="date" />
            </label>
            <label class="field">
              <span>Próxima fecha</span>
              <input v-model="form.nextDate" class="input" type="date" />
            </label>
          </div>

          <button class="btn btn--primary" type="button" :disabled="loading" @click="saveDeworming">
            {{ loading ? 'Guardando...' : 'Guardar desparasitación' }}
          </button>
        </div>
      </section>

      <section class="card table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>Fecha</th>
              <th>Próxima</th>
              <th>Lote</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in dewormingHistory" :key="item.id" class="table__row">
              <td>{{ item.vaccine_name || item.event_type }}</td>
              <td>{{ formatDate(item.applied_date) }}</td>
              <td>{{ item.next_due_date ? formatDate(item.next_due_date) : '—' }}</td>
              <td>{{ item.lot || item.sanitary_batch || '—' }}</td>
            </tr>
            <tr v-if="!dewormingHistory.length">
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
