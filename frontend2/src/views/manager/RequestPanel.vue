<script setup>
import { computed, onMounted } from 'vue';
import { useAppStore } from '@/stores/useAppStore';
import { useToastStore } from '@/stores/useToastStore';
import PageHeader from '@/components/shared/PageHeader.vue';
import DashboardCard from '@/components/shared/DashboardCard.vue';
import { formatMoney } from '@/lib/petcare';

const appStore = useAppStore();
const toastStore = useToastStore();

onMounted(async () => {
  try {
    await Promise.all([
      appStore.fetchRequisitions(),
      appStore.fetchInventory()
    ]);
  } catch (err) {
    console.error('Error fetching data in request panel:', err);
  }
});

// 1. Relación reactiva de solicitudes en el Store
const solicitudes = computed(() => appStore.requisitions);

// Filtramos las que están estrictamente 'Pendientes' para la toma de decisiones
const solicitudesPendientes = computed(() => 
  solicitudes.value.filter(s => s.estado === 'Pendiente')
);

// Formateador de dinero oficial de PetCare
const formatTotal = (value) =>
  formatMoney(value, { locale: 'en-US', currency: 'USD', maximumFractionDigits: 2 });

// Auxiliar para obtener el nombre del insumo original desde el inventario
const obtenerNombreInsumo = (insumoId) => {
  const insumo = appStore.inventory.find(i => String(i.id) === String(insumoId));
  return insumo ? insumo.name : `Insumo ID #${insumoId}`;
};

// 2. Funcionalidad: Modificar estado en Pinia via API
const procesarSolicitud = async (id, nuevoEstado) => {
  try {
    if (nuevoEstado === 'Aprobada') {
      await appStore.approveRequisition(id);
    } else {
      await appStore.cancelRequisition(id, 'Rechazada por Gerencia');
    }
    
    // Notificación visual del éxito de la operación financiera
    toastStore.push({
      title: `Solicitud ${nuevoEstado}`,
      description: `La solicitud ${id} ha sido marcada como ${nuevoEstado.toLowerCase()} en el servidor.`,
      type: nuevoEstado === 'Aprobada' ? 'success' : 'warning',
    });
  } catch (error) {
    console.error(error);
    const detail = error.response?.data?.error || error.response?.data?.detail || 'Hubo un error al actualizar la solicitud en el servidor.';
    toastStore.push({
      title: 'Error de aprobación',
      description: detail,
      type: 'error',
    });
  }
};
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Aprobacion de Inventario"
      subtitle="Bandeja de solicitudes por reabastecimiento."
    />

    <DashboardCard title="Solicitudes Pendientes de Revisión" icon="clipboard-check">
      <div v-if="solicitudesPendientes.length > 0" class="manager-grid">
        
        <article 
          v-for="solicitud in solicitudesPendientes" 
          :key="solicitud.id" 
          class="request-card"
        >
          <header class="request-card__header">
            <div>
              <span class="request-card__id">{{ solicitud.id }}</span>
              <p class="request-card__date">Fecha de emisión: {{ solicitud.fecha }}</p>
            </div>
            <div class="request-card__badge-pending">Pendiente de Firma</div>
          </header>

          <section class="request-card__body">
            <h4>Detalle del Pedido:</h4>
            <ul class="items-list">
              <li v-for="item in solicitud.items" :key="item.insumoId" class="item-row">
                <span>• {{ obtenerNombreInsumo(item.insumoId) }}</span>
                <span class="item-quantity">Cantidad: <strong>{{ item.quantity }} uds.</strong></span>
              </li>
            </ul>
          </section>

          <footer class="request-card__footer">
            <div class="total-box">
              <span class="total-box__label">Costo Total Estimado:</span>
              <span class="total-box__value">{{ formatTotal(solicitud.total) }}</span>
            </div>

            <div class="actions-group">
              <button 
                type="button" 
                class="btn btn--danger-action" 
                @click="procesarSolicitud(solicitud.id, 'Rechazada')"
              >
                Rechazar
              </button>
              <button 
                type="button" 
                class="btn btn--success-action" 
                @click="procesarSolicitud(solicitud.id, 'Aprobada')"
              >
                Aprobar Solicitud
              </button>
            </div>
          </footer>
        </article>

      </div>

      <div v-else class="empty-manager-state">
        <p>No hay solicitudes de reabastecimiento pendientes de revisión financiera.</p>
      </div>
    </DashboardCard>
  </div>
</template>

<style scoped>
.manager-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 20px;
}

.request-card {
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 8px;
  padding: 20px;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.request-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 12px;
}

.request-card__id {
  font-weight: 700;
  font-size: 1.1rem;
  color: #1e293b;
}

.request-card__date {
  font-size: 0.85rem;
  color: #64748b;
  margin: 4px 0 0 0;
}

.request-card__badge-pending {
  background-color: #fef3c7;
  color: #d97706;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
}

.request-card__body {
  padding: 16px 0;
}

.request-card__body h4 {
  margin: 0 0 10px 0;
  font-size: 0.95rem;
  color: #475569;
}

.items-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.item-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 0.9rem;
  color: #334155;
  border-bottom: 1px dashed #f1f5f9;
}

.item-quantity {
  color: #64748b;
}

.request-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.total-box {
  display: flex;
  flex-direction: column;
}

.total-box__label {
  font-size: 0.8rem;
  color: #64748b;
}

.total-box__value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #0f172a;
}

.actions-group {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  transition: background 0.2s ease;
}

.btn--success-action {
  background-color: #2ecc71;
  color: white;
}

.btn--success-action:hover {
  background-color: #27ae60;
}

.btn--danger-action {
  background-color: #e74c3c;
  color: white;
}

.btn--danger-action:hover {
  background-color: #c0392b;
}

.empty-manager-state {
  padding: 60px 20px;
  text-align: center;
  color: #64748b;
  font-style: italic;
}
</style>