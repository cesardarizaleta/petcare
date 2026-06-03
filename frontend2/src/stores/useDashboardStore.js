import { defineStore } from 'pinia';
import { ref } from 'vue';
import http from '@/lib/http';

export const useDashboardStore = defineStore('dashboard', () => {
  const kpis = ref([]);
  const revenueData = ref([]);
  const isLoading = ref(false);
  const hasData = ref(true);

  const fetchDashboardData = async (periodo = 'este_mes', fromDate = null, toDate = null) => {
    isLoading.value = true;
    try {
      const params = { periodo };
      if (fromDate) params.from = fromDate;
      if (toDate) params.to = toDate;

      const res = await http.get('/api/v1/reporting/dashboard/', { params });
      
      kpis.value = res.data.kpis || [];
      revenueData.value = res.data.revenueData || [];
      hasData.value = res.data.has_data;
    } catch (e) {
      console.error('Error fetching dashboard statistics from backend API:', e);
      hasData.value = false;
      kpis.value = [];
      revenueData.value = [];
    } finally {
      isLoading.value = false;
    }
  };

  const exportReport = async (formato = 'csv', periodo = 'este_mes', fromDate = null, toDate = null) => {
    try {
      const params = {
        export_format: formato,
        periodo
      };
      if (fromDate) params.from = fromDate;
      if (toDate) params.to = toDate;

      const response = await http.get('/api/v1/reporting/export/', {
        params,
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      // Extract filename if returned
      const contentDisposition = response.headers['content-disposition'];
      let fileName = `reporte_desempeno_${periodo}.${formato}`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match && match[1]) {
          fileName = match[1];
        }
      }

      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      return true;
    } catch (e) {
      console.error('Error exporting performance report:', e);
      throw e;
    }
  };

  return { kpis, revenueData, isLoading, hasData, fetchDashboardData, exportReport };
});
