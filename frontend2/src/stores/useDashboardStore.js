import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAppStore } from './useAppStore';

export const useDashboardStore = defineStore('dashboard', () => {
  const appStore = useAppStore();

  const kpis = ref([]);
  const revenueData = ref([]);
  const isLoading = ref(false);
  const hasData = ref(true);

  const fetchDashboardData = async (periodo = 'este_mes') => {
    isLoading.value = true;

    try {
      await Promise.all([
        appStore.fetchAppointments(),
        appStore.fetchInventory(),
        appStore.fetchRequisitions()
      ]);
    } catch (e) {
      console.error('Error fetching general dashboard dependencies:', e);
    }

    setTimeout(() => {
      const hoy = new Date();
      const year = hoy.getFullYear();
      const month = String(hoy.getMonth() + 1).padStart(2, '0');
      const day = String(hoy.getDate()).padStart(2, '0');

      const hoyStr = `${year}-${month}-${day}`;
      const mesActual = `${year}-${month}`;

      const hace7Dias = new Date(hoy);
      hace7Dias.setDate(hoy.getDate() - 7);

      // 1. Filtrar citas por periodo
      let citasFiltradas = appStore.appointments;
      if (periodo === 'hoy') {
        citasFiltradas = citasFiltradas.filter((cita) => cita.date === hoyStr);
      } else if (periodo === 'esta_semana') {
        citasFiltradas = citasFiltradas.filter((cita) => new Date(cita.date) >= hace7Dias);
      } else if (periodo === 'este_mes') {
        citasFiltradas = citasFiltradas.filter((cita) => cita.date.startsWith(mesActual));
      }

      // 2. Filtrar requisiciones (compras) por periodo para gasto real y gráfico
      let requisicionesFiltradas = appStore.requisitions;
      if (periodo === 'hoy') {
        requisicionesFiltradas = requisicionesFiltradas.filter((req) => req.fecha === hoyStr);
      } else if (periodo === 'esta_semana') {
        requisicionesFiltradas = requisicionesFiltradas.filter((req) => new Date(req.fecha) >= hace7Dias);
      } else if (periodo === 'este_mes') {
        requisicionesFiltradas = requisicionesFiltradas.filter((req) => req.fecha.startsWith(mesActual));
      }

      // 3. Agrupar gasto de requisiciones por fecha para el gráfico de barras/líneas
      const groupedRevenue = {};
      requisicionesFiltradas.forEach(req => {
        const dateStr = req.fecha;
        if (!dateStr) return;
        
        let key = dateStr;
        if (periodo === 'este_mes') {
          key = dateStr.slice(0, 7); // YYYY-MM
        }
        
        groupedRevenue[key] = (groupedRevenue[key] || 0) + req.total;
      });

      const chartPoints = Object.entries(groupedRevenue).map(([label, amount]) => ({
        label,
        amount: parseFloat(amount.toFixed(2))
      })).sort((a, b) => a.label.localeCompare(b.label));

      revenueData.value = chartPoints.length > 0 ? chartPoints : [
        { label: 'Sin compras', amount: 0 }
      ];

      // 4. Evaluar si hay datos en absoluto (si no hay citas ni requisiciones)
      if (citasFiltradas.length === 0 && requisicionesFiltradas.length === 0) {
        hasData.value = false;
        kpis.value = [];
        isLoading.value = false;
        return;
      }

      hasData.value = true;

      // KPI: Presupuesto Compras (Gasto real acumulado en requisiciones)
      const totalGastoRequisiciones = requisicionesFiltradas.reduce((sum, req) => sum + req.total, 0);

      // KPI: Desabastecimiento de Insumos (Real de inventario)
      const insumosCriticos = appStore.inventory.filter(
        (item) => item.quantity <= item.min_stock
      ).length;

      // KPI: Consultas Realizadas
      const totalCitas = citasFiltradas.length;
      const citasCompletadas = citasFiltradas.filter((cita) => cita.status === 'completed').length;

      // KPI: Consumo Inventario Real (diferencia entre lote initial_stock y current_stock)
      let totalConsumido = 0;
      appStore.inventory.forEach(item => {
        (item.batches || []).forEach(b => {
          const initial = Number(b.initialStock) || 0;
          const current = Number(b.quantity) || 0;
          if (initial > current) {
            totalConsumido += (initial - current);
          }
        });
      });

      // KPI: Efectividad de Citas
      const porcentajeCitas = totalCitas > 0 ? Math.round((citasCompletadas / totalCitas) * 100) : 0;

      kpis.value = [
        {
          id: 'brecha',
          title: 'Presupuesto de Compras',
          value: `$${totalGastoRequisiciones.toFixed(2)}`,
          icon: 'layout-dashboard',
          status: totalGastoRequisiciones > 1000 ? 'warning' : 'success',
        },
        {
          id: 'stock',
          title: 'Desabastecimiento',
          value: insumosCriticos.toString(),
          icon: 'clipboard-list',
          status: insumosCriticos > 0 ? 'danger' : 'success',
        },
        {
          id: 'ingresos',
          title: 'Consultas Realizadas',
          value: citasCompletadas.toString(),
          icon: 'clipboard-check',
          status: 'success',
        },
        {
          id: 'consumo',
          title: 'Consumo Inventario',
          value: totalConsumido.toString(),
          icon: 'syringe',
          status: 'info',
        },
        {
          id: 'citas',
          title: 'Efectividad Citas',
          value: `${porcentajeCitas}%`,
          icon: 'calendar-days',
          status: porcentajeCitas > 50 ? 'success' : 'warning',
        },
      ];

      isLoading.value = false;
    }, 1000);
  };

  return { kpis, revenueData, isLoading, hasData, fetchDashboardData };
});
