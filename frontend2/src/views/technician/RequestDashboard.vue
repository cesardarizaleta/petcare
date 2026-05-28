<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAppStore } from '@/stores/useAppStore';
import PageHeader from '@/components/shared/PageHeader.vue';
import DashboardCard from '@/components/shared/DashboardCard.vue';
import { formatMoney } from '@/lib/petcare';

const appStore = useAppStore();

onMounted(async () => {
  try {
    await appStore.fetchRequisitions();
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

const formatTotal = (value) =>
  formatMoney(value, { locale: 'en-US', currency: 'USD', maximumFractionDigits: 2 });

const getBadgeClass = (estado) => {
  if (estado === 'Pendiente') return 'badge--warning';
  if (estado === 'Aprobada') return 'badge--success';
  if (estado === 'Rechazada') return 'badge--danger';
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
        <label for="filtro-estado">Filtrar por estado:</label>
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
              <th>ID solicitud</th>
              <th>Fecha</th>
              <th>Cantidad de productos</th>
              <th>Costo total estimado</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="solicitud in solicitudesFiltradas" :key="solicitud.id" class="table__row">
              <td>#{{ solicitud.id }}</td>
              <td>{{ solicitud.fecha }}</td>
              <td>{{ solicitud.cantidadProductos }} uds.</td>
              <td>{{ formatTotal(solicitud.total) }}</td>
              <td>
                <span :class="['badge', getBadgeClass(solicitud.estado)]">
                  {{ solicitud.estado }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <p v-else class="empty-state">
        No se encontraron solicitudes con el estado seleccionado.
      </p>
    </DashboardCard>
  </div>
</template>

<style scoped>
.filter-container {
  display: flex;
  align-items: center;
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

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  display: inline-block;
}

.badge--warning {
  background-color: #f39c12;
  color: white;
}

.badge--success {
  background-color: #2ecc71;
  color: white;
}

.badge--danger {
  background-color: #e74c3c;
  color: white;
}
</style>
