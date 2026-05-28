<template>
  <div class="dashboard-container">
    <PageHeader title="Tablero Gerencial" subtitle="Situación operativa y táctica de la clínica" />

    <div class="filter-bar">
      <select
        @change="(e) => dashboardStore.fetchDashboardData(e.target.value)"
        class="gerencia-select"
      >
        <option value="este_mes">Período: Este Mes</option>
        <option value="esta_semana">Período: Esta Semana</option>
        <option value="hoy">Período: Hoy</option>
      </select>
    </div>

    <div v-if="dashboardStore.isLoading" class="kpi-grid">
      <KpiCardSkeleton v-for="i in 5" :key="i" />
    </div>

    <div v-else-if="!dashboardStore.hasData" class="empty-state">
      <div class="text-gray-400 mb-2">
        <svg class="w-16 h-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900">Aún no hay actividad registrada</h3>
      <p class="text-sm text-gray-500 mt-1">Intenta seleccionando un rango de fechas diferente.</p>
    </div>

    <div v-else>
      <div class="kpi-grid">
        <StatCard
          v-for="kpi in dashboardStore.kpis"
          :key="kpi.id"
          :label="kpi.title"
          :value="kpi.value"
          :icon="kpi.icon"
          :toneClass="kpi.status === 'danger' ? 'chip--danger' : 'chip--brand'"
        />
      </div>

      <RevenueChart :data="dashboardStore.revenueData" />
    </div>
  </div>
</template>

<script setup>
  import { onMounted } from 'vue';
  import { useDashboardStore } from '@/stores/useDashboardStore';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatCard from '@/components/shared/StatCard.vue';
  import KpiCardSkeleton from '@/components/dashboard/KpiCardSkeleton.vue';
  import RevenueChart from '@/components/dashboard/RevenueChart.vue';
  const dashboardStore = useDashboardStore();

  onMounted(() => {
    dashboardStore.fetchDashboardData();
  });
</script>

<style scoped>
  .dashboard-container {
    padding: 1.5rem;
  }

  .filter-bar {
    display: flex;
    justify-content: flex-start;
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .gerencia-select {
    appearance: none;
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 0.5rem 2.5rem 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
    cursor: pointer;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    outline: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236b7280'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.75rem center;
    background-size: 1rem;
  }

  .gerencia-select:focus {
    border-color: #7aa250;
    box-shadow: 0 0 0 2px rgba(122, 162, 80, 0.2);
  }

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.5rem;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 0;
    text-align: center;
  }
</style>
