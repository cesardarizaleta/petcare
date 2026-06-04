<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAppStore } from '@/stores/useAppStore';
import PageHeader from '@/components/shared/PageHeader.vue';
import DashboardCard from '@/components/shared/DashboardCard.vue';
import { formatMoney } from '@/lib/petcare';

const appStore = useAppStore();

const itemsPerPage = 5;
const currentPage = ref(1);

onMounted(async () => {
  try {
    await Promise.all([
      appStore.fetchRequisitions(),
      appStore.fetchInventory()
    ]);
  } catch (err) {
    console.error('Error fetching requisitions in RequestDashboard:', err);
  }
});

const solicitudes = computed(() => appStore.requisitions);
const filtroEstado = ref('Todos');

const solicitudesFiltradas = computed(() => {
  if (filtroEstado.value === 'Todos') return solicitudes.value;
  return solicitudes.value.filter((s) => s.estado === filtroEstado.value);
});

const totalPages = computed(() => Math.ceil(solicitudesFiltradas.value.length / itemsPerPage));

const paginatedSolicitudes = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return solicitudesFiltradas.value.slice(start, start + itemsPerPage);
});

watch([filtroEstado, solicitudes], () => {
  currentPage.value = 1;
});

const formatTotal = (value) =>
  formatMoney(value, { locale: 'en-US', currency: 'USD', maximumFractionDigits: 2 });

const obtenerNombreInsumo = (insumoId) => {
  const insumo = appStore.inventory.find(i => String(i.id) === String(insumoId));
  return insumo ? insumo.name : `Insumo ID #${insumoId}`;
};

const formatShortId = (id) => {
  if (!id) return '';
  const str = String(id).replace(/^#/, '');
  return str.length > 8 ? `#${str.slice(0, 8)}...` : `#${str}`;
};

const getBadgeClass = (estado) => {
  if (estado === 'Pendiente') return 'chip--warning';
  if (estado === 'Aprobada') return 'chip--success';
  if (estado === 'Rechazada') return 'chip--danger';
  return '';
};
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Panel de Seguimiento de Solicitudes"
      subtitle="Historial de pedidos enviados al gerente y su estado de aprobación."
    />

    <DashboardCard title="Historial de solicitudes enviadas" icon="clipboard-list">
      <div class="filter-container">
        <label for="filtro-estado" class="field__label">Filtrar por estado:</label>
        <select id="filtro-estado" v-model="filtroEstado" class="select filter-select">
          <option value="Todos">Mostrar todas</option>
          <option value="Pendiente">Pendiente</option>
          <option value="Aprobada">Aprobada</option>
          <option value="Rechazada">Rechazada</option>
        </select>
      </div>

      <section v-if="solicitudesFiltradas.length > 0" class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th class="col-id">ID solicitud</th>
              <th class="col-date">Fecha</th>
              <th class="col-products">Productos solicitados (Nombre e ID)</th>
              <th class="col-qty text-right">Cantidad total</th>
              <th class="col-total text-right">Costo total estimado</th>
              <th class="col-status text-center">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="solicitud in paginatedSolicitudes" :key="solicitud.id" class="table__row">
              <td class="col-id">
                <span class="uuid-tag" :title="solicitud.id">{{ formatShortId(solicitud.id) }}</span>
              </td>
              <td class="col-date">
                <span class="date-text">{{ solicitud.fecha }}</span>
              </td>
              <td class="col-products">
                <div class="products-list">
                  <div v-for="item in solicitud.items" :key="item.insumoId" class="product-item">
                    <div class="product-info">
                      <span class="product-name">{{ obtenerNombreInsumo(item.insumoId) }}</span>
                      <span class="product-id-tag" :title="item.insumoId">ID: {{ formatShortId(item.insumoId) }}</span>
                    </div>
                    <span class="product-qty">{{ item.quantity }} uds.</span>
                  </div>
                </div>
              </td>
              <td class="col-qty text-right text-strong">{{ solicitud.cantidadProductos }} uds.</td>
              <td class="col-total text-right text-strong price-text">{{ formatTotal(solicitud.total) }}</td>
              <td class="col-status text-center">
                <span :class="['chip', getBadgeClass(solicitud.estado)]">
                  {{ solicitud.estado }}
                </span>
              </td>
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
        No se encontraron solicitudes con el estado seleccionado.
      </p>
    </DashboardCard>
  </div>
</template>

<style scoped>
.select,
.input,
.textarea {
  max-width: 100%;
  min-width: 0;
}

.filter-container {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin: 20px 0;
}

.filter-select {
  max-width: 200px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: rgba(61, 61, 61, 0.6);
}

.stack > * {
  min-width: 0;
  max-width: 100%;
}

.table-wrap {
  display: block;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
}

/* Column Widths & Alignments */
.col-id {
  width: 140px;
  white-space: nowrap;
}

.col-date {
  width: 120px;
}

.col-products {
  /* products column can take the remaining space */
}

.col-qty {
  width: 150px;
}

.col-total {
  width: 180px;
}

.col-status {
  width: 140px;
}

.text-right {
  text-align: right !important;
}

.text-center {
  text-align: center !important;
}

.text-strong {
  font-weight: 600;
  color: var(--text-strong);
}

/* UUID Tag styling */
.uuid-tag {
  font-family: monospace;
  font-weight: 600;
  color: var(--brand-strong);
  background: rgba(194, 167, 105, 0.1);
  padding: 3px 8px;
  border-radius: 6px;
  cursor: help;
  font-size: 0.85rem;
  display: inline-block;
  border: 1px solid rgba(194, 167, 105, 0.2);
  transition: all 0.15s ease;
}

.uuid-tag:hover {
  background: rgba(194, 167, 105, 0.18);
  border-color: var(--brand);
}

/* Date text */
.date-text {
  font-size: 0.9rem;
  color: var(--text);
  font-weight: 500;
}

/* Products List Cell */
.products-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 280px;
}

.product-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: rgba(247, 241, 230, 0.4);
  padding: 6px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  transition: background-color 0.15s ease;
}

.product-item:hover {
  background: rgba(247, 241, 230, 0.7);
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.product-name {
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text-strong);
  overflow-wrap: anywhere;
  word-break: break-word;
}

.product-id-tag {
  font-family: monospace;
  font-size: 0.72rem;
  color: rgba(61, 61, 61, 0.55);
  background: rgba(0, 0, 0, 0.04);
  padding: 1px 6px;
  border-radius: 4px;
  align-self: flex-start;
  cursor: help;
}

.product-qty {
  font-weight: 700;
  color: var(--sage-strong);
  background: rgba(165, 186, 142, 0.12);
  border: 1px solid rgba(165, 186, 142, 0.25);
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.75rem;
  white-space: nowrap;
}

/* Price text formatting */
.price-text {
  font-family: monospace;
  font-size: 0.95rem;
  letter-spacing: -0.01em;
}

/* Responsive Overrides */
@media (max-width: 600px) {
  .products-list {
    min-width: 200px;
  }
}

@media (max-width: 480px) {
  :deep(.card) {
    padding: 16px !important;
  }

  :deep(.page-header) {
    padding: 16px !important;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  :deep(.page-header__subtitle) {
    margin-left: 0 !important;
  }

  .filter-container {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .filter-select {
    max-width: 100%;
  }
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
