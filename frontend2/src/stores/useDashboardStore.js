import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAppStore } from './useAppStore';
import { revenueHistory } from '../data/mockData';

export const useDashboardStore = defineStore('dashboard', () => {
  const appStore = useAppStore();

  const kpis = ref([]);
  const revenueData = ref([]);
  const isLoading = ref(false);
  const hasData = ref(true);

  const fetchDashboardData = async (periodo = 'este_mes') => {
    isLoading.value = true;

    //Simular el tiempo de respuesta del servidor (1 segundo)
    setTimeout(() => {
      // 1. Obtener las fechas de control del sistema (Respetando zona horaria local)
      const hoy = new Date();

      const year = hoy.getFullYear();
      const month = String(hoy.getMonth() + 1).padStart(2, '0');
      const day = String(hoy.getDate()).padStart(2, '0');

      const hoyStr = `${year}-${month}-${day}`; // Ahora sí será estrictamente 2026-05-26
      const mesActual = `${year}-${month}`;

      const hace7Dias = new Date(hoy);
      hace7Dias.setDate(hoy.getDate() - 7);

      //Filtrar tanto las operaciones como el historial de ingresos por periodo
      let citasFiltradas = appStore.appointments;

      if (periodo === 'hoy') {
        citasFiltradas = citasFiltradas.filter((cita) => cita.date === hoyStr);
        revenueData.value = revenueHistory.hoy;
      } else if (periodo === 'esta_semana') {
        citasFiltradas = citasFiltradas.filter((cita) => new Date(cita.date) >= hace7Dias);
        revenueData.value = revenueHistory.esta_semana;
      } else if (periodo === 'este_mes') {
        citasFiltradas = citasFiltradas.filter((cita) => cita.date.startsWith(mesActual));
        revenueData.value = revenueHistory.este_mes;
      }

      //Evaluar si hay actividad operativa hoy
      if (citasFiltradas.length === 0) {
        hasData.value = false;
        kpis.value = [];
        revenueData.value = []; //no hay actividad registrada
        isLoading.value = false;
        return;
      }

      hasData.value = true;

      //Desabastecimiento de Insumos
      const insumosCriticos = appStore.inventory.filter(
        (item) => item.quantity <= item.umbral
      ).length;

      //Eficiencia de Citas
      const totalCitas = citasFiltradas.length;
      const citasCompletadas = citasFiltradas.filter((cita) => cita.status === 'completed').length;

      const porcentajeCitas =
        totalCitas > 0 ? Math.round((citasCompletadas / totalCitas) * 100) : 0;

      //Métricas financieras
      const ingresosSimulados = citasCompletadas * 150;
      const brechaActual = 810 - citasCompletadas * 50;

      kpis.value = [
        {
          id: 'brecha',
          title: 'Brecha de Ingresos',
          value: `$${brechaActual > 0 ? brechaActual : 0}`,
          icon: 'layout-dashboard',
          status: 'warning',
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
          title: 'Ingresos Percibidos',
          value: `$${ingresosSimulados}`,
          icon: 'clipboard-check',
          status: 'success',
        },
        {
          id: 'consumo',
          title: 'Consumo Inventario',
          value: '45',
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

  //Retornamos revenueData junto con los demás estados para que la vista pueda leerlo
  return { kpis, revenueData, isLoading, hasData, fetchDashboardData };
});
