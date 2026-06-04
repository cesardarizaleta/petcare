<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import PageHeader from '@/components/shared/PageHeader.vue';
import DashboardCard from '@/components/shared/DashboardCard.vue';
import { useAppStore } from '@/stores/useAppStore';
import { useToastStore } from '@/stores/useToastStore';

const appStore = useAppStore();
const toastStore = useToastStore();
const loading = ref(false);
const errorMessage = ref('');

const selectedRequisitionId = ref('');
const itemsToReceive = ref([]);
const observations = ref('');

const today = new Date().toISOString().split('T')[0];
const open = ref(true);

onMounted(async () => {
  try {
    await Promise.all([
      appStore.fetchInventory(),
      appStore.fetchRequisitions()
    ]);
  } catch (err) {
    console.error('Error fetching inventory/requisitions in RepositionStock:', err);
  }
});

const solicitudesAprobadas = computed(() => 
  appStore.requisitions.filter(r => r.estado === 'Aprobada')
);

const generateLotNumber = () => {
  const todayStr = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const rand = Math.floor(100 + Math.random() * 900);
  return `LOT-${todayStr}-${rand}`;
};

watch(selectedRequisitionId, (newId) => {
  if (!newId) {
    itemsToReceive.value = [];
    return;
  }
  const req = solicitudesAprobadas.value.find(r => r.id === newId);
  if (req) {
    itemsToReceive.value = req.items.map(item => ({
      itemId: item.id,
      insumoId: item.insumoId,
      supplyName: item.supplyName,
      supplySku: item.supplySku,
      quantityRequested: item.quantity,
      quantityReceived: item.quantity,
      expirationDate: '',
      lotNumber: generateLotNumber(),
    }));
  } else {
    itemsToReceive.value = [];
  }
});

watch(
  itemsToReceive,
  () => {
    errorMessage.value = '';
  },
  { deep: true }
);

watch(
  selectedRequisitionId,
  () => {
    errorMessage.value = '';
  }
);

const preventNegative = (e) => {
  if (e.key === '-' || e.key === '+' || e.key === 'e' || e.key === 'E') {
    e.preventDefault();
  }
};

const mapKey = (key) => {
  const dict = {
    batch: 'Número de lote',
    expiration_date: 'Fecha de vencimiento',
    expirationDate: 'Fecha de vencimiento',
    quantity: 'Cantidad',
    insumoId: 'Insumo',
    insumo: 'Insumo',
  };
  return dict[key] || key;
};

const getErrorMessage = (error) => {
  const data = error?.response?.data;
  if (!data) return error?.message || 'Hubo un error al registrar el lote en el servidor.';
  
  if (typeof data === 'string') return data;
  if (data.error) return data.error;
  if (data.detail) return data.detail;
  if (data.message) return data.message;

  if (typeof data === 'object') {
    const fieldErrors = Object.entries(data)
      .filter(([key, v]) => key !== 'error' && key !== 'detail' && key !== 'message' && (Array.isArray(v) || typeof v === 'string'))
      .map(([key, val]) => {
        const fieldName = mapKey(key);
        const msgs = Array.isArray(val) ? val.join(', ') : val;
        return `${fieldName}: ${msgs}`;
      })
      .join('\n');
    if (fieldErrors) return fieldErrors;

    if (data.non_field_errors) return data.non_field_errors.join(', ');
  }

  return 'Hubo un error al registrar el lote en el servidor.';
};

const resetForm = () => {
  selectedRequisitionId.value = '';
  itemsToReceive.value = [];
  observations.value = '';
  errorMessage.value = '';
};

const guardarEntrada = async () => {
  errorMessage.value = '';

  if (!selectedRequisitionId.value) {
    errorMessage.value = 'Debe seleccionar una solicitud de stock aprobada.';
    return;
  }

  for (const item of itemsToReceive.value) {
    if (!item.expirationDate) {
      errorMessage.value = `Debe especificar la fecha de vencimiento para ${item.supplyName}.`;
      return;
    }
    if (!item.lotNumber) {
      errorMessage.value = `Debe especificar el número de lote para ${item.supplyName}.`;
      return;
    }
    const qty = Number(item.quantityReceived);
    if (isNaN(qty) || qty <= 0) {
      errorMessage.value = `La cantidad recibida para ${item.supplyName} debe ser mayor a 0.`;
      return;
    }
  }

  loading.value = true;
  try {
    const payloadItems = itemsToReceive.value.map(item => ({
      itemId: item.itemId,
      lotNumber: item.lotNumber,
      expirationDate: item.expirationDate,
      quantityReceived: item.quantityReceived,
    }));

    await appStore.receiveRequisition(selectedRequisitionId.value, payloadItems);

    toastStore.push({
      title: 'Reposición registrada',
      description: 'La mercancía ha sido ingresada exitosamente al inventario.',
      type: 'success',
    });

    resetForm();
  } catch (error) {
    console.error(error);
    errorMessage.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Reposición de Stock"
      subtitle="Registro de entrada de mercancía a partir de solicitudes aprobadas."
    />

    <DashboardCard title="Entrada por lote aprobado" icon="notebook-pen">
      <form v-show="open" class="stack form-section" @submit.prevent="guardarEntrada">
        <div class="field">
          <label for="solicitud">Seleccionar solicitud aprobada*</label>
          <select id="solicitud" v-model="selectedRequisitionId" class="select" required>
            <option value="" disabled>Seleccione una solicitud aprobada (gerente)...</option>
            <option v-for="req in solicitudesAprobadas" :key="req.id" :value="req.id">
              Solicitud #{{ req.id.slice(0, 8) }}... - {{ req.fecha }} ({{ req.cantidadProductos }} uds.)
            </option>
          </select>
        </div>

        <div v-if="itemsToReceive.length > 0" class="stack items-section">
          <div class="section-title-bar">
            <h3 class="section-title">Detalle de Insumos Recibidos</h3>
            <span class="badge">{{ itemsToReceive.length }} Insumos</span>
          </div>

          <div v-for="(item, idx) in itemsToReceive" :key="item.itemId" class="item-receive-card">
            <div class="item-header">
              <span class="item-sku">{{ item.supplySku || 'SKU-N/A' }}</span>
              <h4 class="item-name">{{ item.supplyName }}</h4>
            </div>
            
            <div class="grid-fields">
              <div class="field">
                <label :for="'cant-' + idx">Cantidad Recibida (Bloqueado)</label>
                <div class="input-lock-wrapper">
                  <input
                    :id="'cant-' + idx"
                    :value="item.quantityReceived"
                    type="number"
                    class="input input--disabled"
                    disabled
                  />
                  <span class="lock-icon">🔒</span>
                </div>
              </div>

              <div class="field">
                <label :for="'caducidad-' + idx">Fecha de vencimiento (Obligatoria)*</label>
                <input
                  :id="'caducidad-' + idx"
                  v-model="item.expirationDate"
                  type="date"
                  :min="today"
                  class="input input--required"
                  required
                />
              </div>

              <div class="field">
                <label :for="'lote-' + idx">Número de lote (Bloqueado)</label>
                <div class="input-lock-wrapper">
                  <input
                    :id="'lote-' + idx"
                    :value="item.lotNumber"
                    type="text"
                    class="input input--disabled"
                    disabled
                  />
                  <span class="lock-icon">🔒</span>
                </div>
              </div>
            </div>
          </div>

          <div class="field observations-field">
            <label for="observaciones">Observaciones de la Recepción</label>
            <textarea
              class="textarea"
              id="observaciones"
              v-model="observations"
              placeholder="Escriba comentarios sobre el estado físico de la entrega, temperatura de llegada, detalles del transportista, etc."
            />
          </div>
        </div>

        <p v-if="solicitudesAprobadas.length === 0" class="empty-state">
          No hay solicitudes de reabastecimiento aprobadas por el gerente pendientes de recepción.
        </p>

        <div v-if="errorMessage" class="error-message-block">
          <svg class="error-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <div class="error-text">{{ errorMessage }}</div>
        </div>

        <button v-if="itemsToReceive.length > 0" class="btn btn--primary" type="submit" :disabled="loading">
          {{ loading ? 'Registrando entrada...' : 'Registrar entrada de mercancía' }}
        </button>
      </form>
    </DashboardCard>
  </div>
</template>

<style scoped>
.form-section {
  margin-top: 28px;
}

.items-section {
  margin-top: 24px;
  gap: 20px;
}

.section-title-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--border);
  padding-bottom: 8px;
  margin-bottom: 8px;
}

.section-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-strong);
  margin: 0;
}

.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 9999px;
  background-color: rgba(194, 167, 105, 0.1);
  color: var(--brand-strong);
}

.item-receive-card {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  background: var(--surface-strong);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.015);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.item-receive-card:hover {
  border-color: var(--border-strong);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.03);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  border-bottom: 1px dashed var(--border);
  padding-bottom: 12px;
}

.item-sku {
  font-family: monospace;
  font-size: 0.8rem;
  font-weight: 600;
  background-color: var(--surface-soft);
  color: var(--brand-strong);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.item-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-strong);
  margin: 0;
}

.grid-fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.input-lock-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-lock-wrapper .input {
  padding-right: 36px;
}

.lock-icon {
  position: absolute;
  right: 12px;
  font-size: 0.85rem;
  color: rgba(61, 61, 61, 0.4);
  pointer-events: none;
}

.input--disabled {
  background-color: var(--surface-soft) !important;
  border-color: var(--border) !important;
  color: rgba(61, 61, 61, 0.5) !important;
  cursor: not-allowed;
  opacity: 0.85;
}

.input--required {
  border-color: var(--brand);
  background-color: rgba(194, 167, 105, 0.02);
}

.input--required:focus {
  border-color: var(--brand-strong);
  box-shadow: 0 0 0 3px rgba(194, 167, 105, 0.15);
}

.observations-field {
  margin-top: 24px;
  border-top: 1px solid var(--border);
  padding-top: 20px;
}

.textarea {
  min-height: 100px;
  resize: vertical;
}

.empty-state {
  padding: 40px;
  text-align: center;
  background-color: var(--surface-soft);
  border-radius: var(--radius-md);
  color: rgba(61, 61, 61, 0.7);
  font-style: italic;
  border: 1px dashed var(--border-strong);
}

.error-message-block {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background-color: rgba(178, 60, 60, 0.08);
  border: 1px solid var(--danger);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  color: var(--danger);
  font-size: 0.9rem;
  margin-top: 8px;
  margin-bottom: 8px;
}

.error-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  margin-top: 2px;
}

.error-text {
  white-space: pre-line;
  line-height: 1.4;
  font-weight: 500;
}
</style>
