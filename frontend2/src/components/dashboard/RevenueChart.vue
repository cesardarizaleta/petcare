<template>
  <div class="chart-card">
    <div class="chart-header">
      <div class="title-indicator"></div>
      <div class="title-text">
        <h3>Evolución de Ingresos</h3>
        <p>Tendencia financiera del período seleccionado</p>
      </div>
    </div>

    <div class="chart-container">
      <Line v-if="chartData" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
  import { computed } from 'vue';
  import { Line } from 'vue-chartjs';
  import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Filler,
  } from 'chart.js';

  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler);

  const props = defineProps({
    data: {
      type: Array,
      required: true,
      default: () => [],
    },
  });

  //Si cambian los datos del prop, la gráfica se redibuja sola
  const chartData = computed(() => {
    if (!props.data || props.data.length === 0) return null;

    return {
      labels: props.data.map((item) => item.label),
      datasets: [
        {
          label: 'Ingresos',
          data: props.data.map((item) => item.amount),
          borderColor: '#7aa250',
          backgroundColor: 'rgba(122, 162, 80, 0.15)',
          borderWidth: 2,
          pointBackgroundColor: '#ffffff',
          pointBorderColor: '#7aa250',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          fill: true,
          tension: 0.4,
        },
      ],
    };
  });

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#374151',
        padding: 12,
        titleFont: { size: 13 },
        bodyFont: { size: 14, weight: 'bold' },
        displayColors: false,
        callbacks: {
          label: function (context) {
            return '$' + context.parsed.y;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: '#f3f4f6',
          drawBorder: false,
        },
        ticks: {
          color: '#6b7280',
          callback: function (value) {
            return '$' + value;
          },
        },
      },
      x: {
        grid: {
          display: false,
          drawBorder: false,
        },
        ticks: {
          color: '#6b7280',
        },
      },
    },
  };
</script>

<style scoped>
  .chart-card {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 0.75rem;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    border: 1px solid #f3f4f6;
    margin-top: 1.5rem;
  }

  .chart-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }

  .title-indicator {
    width: 6px;
    height: 24px;
    background-color: #7aa250;
    border-radius: 9999px;
  }

  .title-text h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 700;
    color: #1f2937;
    line-height: 1.2;
  }

  .title-text p {
    margin: 0;
    margin-top: 0.25rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: #6b7280;
  }

  .chart-container {
    position: relative;
    height: 18rem;
    width: 100%;
  }
</style>
