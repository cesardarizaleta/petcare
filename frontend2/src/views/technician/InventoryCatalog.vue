<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import PageHeader from '@/components/shared/PageHeader.vue';
import DashboardCard from '@/components/shared/DashboardCard.vue';
import { useAppStore } from '@/stores/useAppStore';
import { useToastStore } from '@/stores/useToastStore';
import { formatMoney } from '@/lib/petcare';
import { evaluateProductAlertState } from '@/lib/inventory';

const appStore = useAppStore();
const toastStore = useToastStore();

const itemsPerPage = 5;
const currentPage = ref(1);

onMounted(async () => {
  try {
    await appStore.fetchInventory();
  } catch (err) {
    console.error('Error fetching inventory in catalog:', err);
  }
});

const inventory = computed(() => appStore.inventory);

const totalPages = computed(() => Math.ceil(inventory.value.length / itemsPerPage));

const paginatedInventory = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return inventory.value.slice(start, start + itemsPerPage);
});

watch(inventory, () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = Math.max(1, totalPages.value);
  }
});

const formatUnitCost = (value) =>
  formatMoney(value, { locale: 'en-US', currency: 'USD', maximumFractionDigits: 2 });

const alertByItemId = computed(() => {
  const map = new Map();
  inventory.value.forEach((item) => {
    map.set(item.id, evaluateProductAlertState(item));
  });
  return map;
});

function handleUmbralChange(item) {
  if (item.min_stock === undefined || item.min_stock === null || item.min_stock === '' || Number(item.min_stock) < 1) {
    toastStore.push({
      title: 'Stock mínimo inválido',
      description: 'El stock mínimo no puede ser negativo o menor a 1. Se ha restablecido a 1.',
      type: 'error'
    });
    item.min_stock = 1;
  } else {
    toastStore.push({
      title: 'Stock mínimo actualizado',
      description: `El stock mínimo para ${item.name} se actualizó a ${item.min_stock} unidades.`,
      type: 'success'
    });
  }
  localStorage.setItem(`inventory_umbral_${item.id}`, item.min_stock);
  appStore.normalizeInventory();
}
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Gestión de Insumos"
      subtitle="Catálogo maestro: existencias, umbrales y alertas de stock o vencimiento."
    />

    <DashboardCard title="Vista General del Inventario" icon="syringe">
      <section v-if="inventory.length > 0" class="table-wrap inventory-table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Nombre del insumo</th>
              <th>Categoría</th>
              <th>Cantidad disponible</th>
              <th>Stock mínimo</th>
              <th>Costo unitario</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in paginatedInventory"
              :key="item.id"
              class="table__row"
              :class="`inventory-row--${alertByItemId.get(item.id)?.alertClass ?? 'normal'}`"
            >
              <td class="inventory-table__name">
                {{ item.name }}
                <span
                  v-if="alertByItemId.get(item.id)?.messages?.length"
                  class="inventory-tooltip"
                  role="tooltip"
                >
                  <span
                    v-for="(line, index) in alertByItemId.get(item.id).messages"
                    :key="index"
                    class="inventory-tooltip__line"
                  >
                    {{ line }}
                  </span>
                </span>
              </td>
              <td>{{ item.type }}</td>
              <td>{{ item.quantity }} uds.</td>
              <td>
                <input
                  v-model.number="item.min_stock"
                  type="number"
                  min="1"
                  class="input inventory-min_stock-input"
                  title="Nivel mínimo de existencias"
                  @change="handleUmbralChange(item)"
                />
              </td>
              <td>{{ formatUnitCost(item.unitCost) }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Controles de Paginación -->
        <div class="pagination-controls" v-if="totalPages > 1">
          <button
            class="btn btn--soft btn--sm"
            type="button"
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            &larr; Anterior
          </button>
          <span class="pagination-info">
            Página <strong>{{ currentPage }}</strong> de <strong>{{ totalPages }}</strong>
          </span>
          <button
            class="btn btn--soft btn--sm"
            type="button"
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            Siguiente &rarr;
          </button>
        </div>
      </section>
      <p v-else class="empty-state">
        No hay insumos en el catálogo. Registre uno desde la sección "Registrar Insumos".
      </p>
    </DashboardCard>
  </div>
</template>

<style scoped>
.inventory-table-wrap {
  margin-top: 1.25rem;
}

.inventory-table__name {
  position: relative;
  font-weight: 500;
}

.inventory-min_stock-input {
  width: 4.5rem;
  padding: 6px 8px;
}

.inventory-row--critical td {
  background-color: #ffebee;
  border-left: 4px solid #f44336;
}

.inventory-row--warning td {
  background-color: #fff8e1;
  border-left: 4px solid #ffc107;
}

.inventory-row--critical .inventory-table__name,
.inventory-row--warning .inventory-table__name {
  cursor: help;
}

.inventory-tooltip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  bottom: 100%;
  left: 0;
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 12rem;
  max-width: 20rem;
  padding: 8px 12px;
  border-radius: 6px;
  background: var(--bg);
  color: var(--text-strong);
  font-size: 13px;
  font-weight: 400;
  line-height: 1.4;
  white-space: normal;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  transition: opacity 0.2s ease, bottom 0.2s ease;
}

.inventory-tooltip__line {
  display: block;
}

.inventory-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 15px;
  border: 5px solid transparent;
  border-top-color: var(--bg);
}

.inventory-row--critical:hover .inventory-tooltip,
.inventory-row--warning:hover .inventory-tooltip {
  visibility: visible;
  opacity: 1;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: rgba(61, 61, 61, 0.6);
}

.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.pagination-info {
  font-family: var(--sans);
  font-size: 0.9rem;
  color: var(--text);
}

.btn--sm {
  padding: 6px 12px;
  font-size: 0.8rem;
}
</style>
