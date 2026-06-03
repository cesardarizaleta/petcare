<template>
  <div class="dashboard-container">
    <PageHeader title="Tablero Gerencial" subtitle="Situación operativa y táctica de la clínica" />

    <!-- Control Toolbar: Period Filters and Report Exports -->
    <div class="toolbar-card card">
      <div class="filter-group">
        <div class="field select-wrapper">
          <label for="filtro-periodo" class="field__label">Período de Análisis</label>
          <select
            id="filtro-periodo"
            v-model="periodo"
            @change="onPeriodoChange"
            class="select period-select"
          >
            <option value="este_mes">Este Mes</option>
            <option value="esta_semana">Esta Semana</option>
            <option value="hoy">Hoy</option>
            <option value="personalizado">Rango Personalizado</option>
          </select>
        </div>

        <transition name="fade">
          <div v-if="periodo === 'personalizado'" class="custom-range-inputs">
            <div class="field">
              <label for="fecha-desde" class="field__label">Desde</label>
              <input
                id="fecha-desde"
                type="date"
                v-model="fechaDesde"
                class="input date-input"
              />
            </div>
            <div class="field">
              <label for="fecha-hasta" class="field__label">Hasta</label>
              <input
                id="fecha-hasta"
                type="date"
                v-model="fechaHasta"
                class="input date-input"
              />
            </div>
            <button @click="aplicarRangoPersonalizado" class="btn btn--primary apply-btn">
              Consultar
            </button>
          </div>
        </transition>
      </div>

      <div class="export-actions">
        <span class="export-label">Reportes del Período</span>
        <div class="btn-group">
          <button 
            @click="exportarReporte('csv')" 
            :disabled="isExportingCsv"
            class="btn btn--ghost export-btn"
          >
            <AppIcon v-if="!isExportingCsv" name="download" :size="16" />
            <span v-else class="loader-spinner"></span>
            Exportar CSV
          </button>
          <button 
            @click="exportarReporte('json')" 
            :disabled="isExportingJson"
            class="btn btn--ghost export-btn"
          >
            <AppIcon v-if="!isExportingJson" name="download" :size="16" />
            <span v-else class="loader-spinner"></span>
            Exportar JSON
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div v-if="dashboardStore.isLoading" class="stack">
      <div class="loading-banner card">
        <span class="spinner-large"></span>
        <div class="loading-text">
          <h3>Cargando información del tablero...</h3>
          <p>Por favor espera un momento mientras calculamos las estadísticas en tiempo real.</p>
        </div>
      </div>
      <div class="kpi-grid">
        <KpiCardSkeleton v-for="i in 5" :key="i" />
      </div>
    </div>

    <div v-else-if="!dashboardStore.hasData" class="empty-state">
      <div class="empty-state-icon">
        <svg class="w-16 h-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 64px; height: 64px; opacity: 0.5;">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>
      <h3 class="empty-state-title">Aún no hay actividad registrada</h3>
      <p class="empty-state-text">Intenta seleccionando un rango de fechas diferente.</p>
    </div>

    <div v-else class="stack">
      <div class="kpi-grid">
        <StatCard
          v-for="kpi in dashboardStore.kpis"
          :key="kpi.id"
          :label="kpi.title"
          :value="kpi.value"
          :icon="kpi.icon"
          :toneClass="getToneClass(kpi.status)"
        />
      </div>

      <RevenueChart :data="dashboardStore.revenueData" />
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue';
  import { useDashboardStore } from '@/stores/useDashboardStore';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatCard from '@/components/shared/StatCard.vue';
  import AppIcon from '@/components/shared/AppIcon.vue';
  import KpiCardSkeleton from '@/components/dashboard/KpiCardSkeleton.vue';
  import RevenueChart from '@/components/dashboard/RevenueChart.vue';

  const dashboardStore = useDashboardStore();

  const periodo = ref('este_mes');
  const fechaDesde = ref('');
  const fechaHasta = ref('');

  const isExportingCsv = ref(false);
  const isExportingJson = ref(false);

  onMounted(() => {
    dashboardStore.fetchDashboardData(periodo.value);
  });

  const onPeriodoChange = () => {
    if (periodo.value !== 'personalizado') {
      dashboardStore.fetchDashboardData(periodo.value);
    }
  };

  const aplicarRangoPersonalizado = () => {
    if (!fechaDesde.value || !fechaHasta.value) return;
    dashboardStore.fetchDashboardData('personalizado', fechaDesde.value, fechaHasta.value);
  };

  const exportarReporte = async (formato) => {
    if (formato === 'csv') isExportingCsv.value = true;
    if (formato === 'json') isExportingJson.value = true;
    
    try {
      const isCustom = periodo.value === 'personalizado';
      await dashboardStore.exportReport(
        formato,
        periodo.value,
        isCustom ? fechaDesde.value : null,
        isCustom ? fechaHasta.value : null
      );
    } catch (err) {
      console.error('Error exporting report:', err);
    } finally {
      if (formato === 'csv') isExportingCsv.value = false;
      if (formato === 'json') isExportingJson.value = false;
    }
  };

  const getToneClass = (status) => {
    if (status === 'danger') return 'chip--danger';
    if (status === 'warning') return 'chip--warning';
    if (status === 'success') return 'chip--success';
    if (status === 'info') return 'chip--sage';
    return 'chip--brand';
  };
</script>

<style scoped>
  .dashboard-container {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .toolbar-card {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 20px;
    padding: 20px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
  }

  .filter-group {
    display: flex;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 16px;
    flex: 1;
  }

  .select-wrapper {
    min-width: 200px;
  }

  .custom-range-inputs {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    animation: slideIn 0.25s ease-out;
  }

  .date-input {
    padding: 0.5rem 0.8rem;
    border-radius: 12px;
    border: 1px solid rgba(194, 167, 105, 0.2);
    min-width: 140px;
    font-size: 0.875rem;
  }

  .apply-btn {
    padding: 0.6rem 1.2rem;
    font-size: 0.875rem;
    border-radius: 999px;
  }

  .export-actions {
    display: flex;
    flex-direction: column;
    gap: 6px;
    align-items: flex-start;
  }

  .export-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    font-weight: 700;
    color: rgba(61, 61, 61, 0.52);
  }

  .btn-group {
    display: flex;
    gap: 10px;
  }

  .export-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0.6rem 1.2rem;
    font-size: 0.875rem;
    border-radius: 999px;
  }

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 0;
    text-align: center;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
  }

  .empty-state-title {
    margin-top: 1rem;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-strong);
  }

  .empty-state-text {
    margin-top: 0.25rem;
    font-size: 0.875rem;
    color: rgba(61, 61, 61, 0.6);
  }

  /* Spinner Loader for Export Buttons */
  .loader-spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid rgba(0, 0, 0, 0.1);
    border-top-color: var(--brand-strong);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  /* Fade transition for Vue */
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.2s ease, transform 0.2s ease;
  }
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
    transform: translateX(-10px);
  }

  /* Loading state styles */
  .loading-banner {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 24px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    animation: fadeIn 0.3s ease;
  }

  .spinner-large {
    display: block;
    width: 32px;
    height: 32px;
    border: 3.5px solid rgba(194, 167, 105, 0.15);
    border-top-color: var(--brand-strong);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .loading-text h3 {
    margin: 0;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-strong);
  }

  .loading-text p {
    margin: 4px 0 0;
    font-size: 0.85rem;
    color: rgba(61, 61, 61, 0.6);
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @media (max-width: 768px) {
    .toolbar-card {
      flex-direction: column;
      align-items: stretch;
    }
    .custom-range-inputs {
      flex-direction: column;
      align-items: stretch;
      width: 100%;
    }
    .export-actions {
      align-items: stretch;
    }
    .btn-group {
      flex-direction: column;
    }
  }
</style>
