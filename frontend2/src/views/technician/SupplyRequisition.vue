<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAppStore } from '@/stores/useAppStore';
import { useToastStore } from '@/stores/useToastStore';
import PageHeader from '@/components/shared/PageHeader.vue';
import DashboardCard from '@/components/shared/DashboardCard.vue';
import { formatMoney } from '@/lib/petcare';

const appStore = useAppStore();
const toastStore = useToastStore();
const loading = ref(false);

onMounted(async () => {
  try {
    await appStore.fetchInventory();
  } catch (err) {
    console.error('Error fetching inventory in supply requisition:', err);
  }
});

const listaInsumos = computed(() => appStore.inventory);

const form = ref({
  insumoId: '',
  quantity: 1,
});

watch(
  listaInsumos,
  (insumos) => {
    if (insumos.length && !form.value.insumoId) {
      form.value.insumoId = insumos[0].id;
    }
  },
  { immediate: true, deep: true }
);

const itemsSolicitados = ref([]);

const getSupplyById = (id) =>
  listaInsumos.value.find((insumo) => String(insumo.id) === String(id));

const getUnitCost = (supply) => (supply ? supply.unitCost ?? 0 : 0);

const formatUnitCost = (value) =>
  formatMoney(value, { locale: 'en-US', currency: 'USD', maximumFractionDigits: 2 });

const agregarInsumoALista = () => {
  if (!form.value.insumoId || form.value.quantity < 1) return;

  const id = String(form.value.insumoId);
  const cantidad = Number(form.value.quantity);
  const existe = itemsSolicitados.value.find((item) => String(item.insumoId) === String(id));

  if (existe) {
    existe.quantity += cantidad;
  } else {
    itemsSolicitados.value.push({ insumoId: id, quantity: cantidad });
  }

  // Pre-select first item again from catalog after reset
  if (listaInsumos.value.length) {
    form.value.insumoId = listaInsumos.value[0].id;
  } else {
    form.value.insumoId = '';
  }
  form.value.quantity = 1;
};

const quitarInsumo = (index) => {
  itemsSolicitados.value.splice(index, 1);
};

const gastoTotalPrevisto = computed(() =>
  itemsSolicitados.value.reduce((total, item) => {
    const supply = getSupplyById(item.insumoId);
    return total + item.quantity * getUnitCost(supply);
  }, 0)
);

const enviarAlGerente = async () => {
  if (itemsSolicitados.value.length === 0) return;

  const nuevaSolicitud = {
    id: `REQ-${Date.now()}`,
    fecha: new Date().toLocaleDateString(),
    cantidadProductos: itemsSolicitados.value.reduce((acc, item) => acc + item.quantity, 0),
    total: gastoTotalPrevisto.value,
    estado: 'Pendiente',
    items: [...itemsSolicitados.value],
  };

  loading.value = true;
  try {
    await appStore.addRequisition(nuevaSolicitud);

    toastStore.push({
      title: 'Solicitud enviada',
      description: 'Estado: Pendiente. El gerente podrá revisarla en su bandeja.',
      type: 'success',
    });

    itemsSolicitados.value = [];
  } catch (error) {
    console.error(error);
    const detail = error.response?.data?.error || error.response?.data?.detail || 'Hubo un error al registrar la orden de compra.';
    toastStore.push({
      title: 'Error al enviar solicitud',
      description: detail,
      type: 'error',
    });
  } finally {
    loading.value = false;
  }
};

</script>

<template>
  <div class="stack">
    <PageHeader
      title="Solicitud de reabastecimiento"
      subtitle="Generación de pedidos al gerente a partir del catálogo maestro."
    />

    <DashboardCard title="Nueva solicitud" icon="notebook-pen">
      <div class="stack form-section">
        <div class="field">
          <label for="insumo">Seleccionar insumo del catálogo*</label>
          <select id="insumo" v-model="form.insumoId" class="select" required>
            <option value="" disabled>Seleccione un insumo del catálogo...</option>
            <option v-for="insumo in listaInsumos" :key="insumo.id" :value="insumo.id">
              {{ insumo.name }} (Stock: {{ insumo.quantity }} uds. | {{ formatUnitCost(insumo.unitCost) }})
            </option>
          </select>
        </div>

        <div class="field">
          <label for="cant">Cantidad deseada*</label>
          <input
            class="input"
            id="cant"
            v-model.number="form.quantity"
            type="number"
            min="1"
            required
            placeholder="1"
          />
        </div>

        <button
          class="btn btn--primary"
          type="button"
          :disabled="!form.insumoId"
          @click="agregarInsumoALista"
        >
          Agregar a la lista
        </button>
      </div>

      <div v-if="itemsSolicitados.length > 0" class="stack request-summary">
        <h3>Detalle de la solicitud actual</h3>

        <section class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Insumo</th>
                <th>Cantidad</th>
                <th>Costo unitario</th>
                <th>Subtotal</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in itemsSolicitados" :key="item.insumoId" class="table__row">
                <td>{{ getSupplyById(item.insumoId)?.name }}</td>
                <td>
                  <input
                    class="input quantity-input"
                    type="number"
                    v-model.number="item.quantity"
                    min="1"
                  />
                </td>
                <td>{{ formatUnitCost(getUnitCost(getSupplyById(item.insumoId))) }}</td>
                <td>
                  {{
                    formatUnitCost(item.quantity * getUnitCost(getSupplyById(item.insumoId)))
                  }}
                </td>
                <td>
                  <button type="button" class="btn btn--danger btn--sm" @click="quitarInsumo(index)">
                    Quitar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        <div class="request-total">
          <span class="request-total__label">Gasto total previsto (precios oficiales):</span>
          <span class="request-total__value">{{ formatUnitCost(gastoTotalPrevisto) }}</span>
        </div>

        <button class="btn btn--primary request-submit" type="button" :disabled="loading" @click="enviarAlGerente">
          {{ loading ? 'Enviando solicitud...' : 'Enviar al gerente' }}
        </button>

      </div>
    </DashboardCard>
  </div>
</template>

<style scoped>
.form-section {
  margin-top: 28px;
}

.request-summary {
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
}

.quantity-input {
  width: 5rem;
  padding: 6px 8px;
}

.request-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 16px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.03);
}

.request-total__label {
  color: rgba(61, 61, 61, 0.7);
}

.request-total__value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-strong);
}

.request-submit {
  align-self: flex-end;
}

.btn--sm {
  padding: 6px 12px;
  font-size: 0.8125rem;
}

.btn--danger {
  background: #e74c3c;
  color: #fff;
  border: none;
}
</style>
