<script setup>
import { ref } from 'vue';
import PageHeader from '@/components/shared/PageHeader.vue';
import DashboardCard from '@/components/shared/DashboardCard.vue';
import { useAppStore } from '@/stores/useAppStore';
import { useToastStore } from '@/stores/useToastStore';

const CATEGORY_OPTIONS = [
  { value: 'MEDICINE', label: 'Medicamento' },
  { value: 'VACCINE', label: 'Vacuna' },
  { value: 'CONSUMABLE', label: 'Consumible' },
  { value: 'EQUIPMENT', label: 'Equipo' },
];

const EMPTY_FORM = {
  nombre: '',
  categoria: '',
  min_stock: '',
  stock_inicial: 0,
  costo_inicial: '',
  observaciones: '',
};

const appStore = useAppStore();
const toastStore = useToastStore();
const open = ref(true);
const form = ref({ ...EMPTY_FORM });
const loading = ref(false);

const resetForm = () => {
  Object.assign(form.value, EMPTY_FORM);
};

const preventNegative = (e) => {
  if (e.key === '-' || e.key === '+' || e.key === 'e' || e.key === 'E') {
    e.preventDefault();
  }
};

const sanitizeMinStock = () => {
  if (form.value.min_stock === '' || form.value.min_stock === null) return;
  const val = Number(form.value.min_stock);
  if (val < 1) {
    form.value.min_stock = 1;
  } else if (val > 100000) {
    form.value.min_stock = 100000;
  }
};

const sanitizeStockInicial = () => {
  if (form.value.stock_inicial === '' || form.value.stock_inicial === null) return;
  const val = Number(form.value.stock_inicial);
  if (val < 0) {
    form.value.stock_inicial = 0;
  } else if (val > 100000) {
    form.value.stock_inicial = 100000;
  }
};

async function handleSubmit() {
  const minStockVal = Number(form.value.min_stock);
  if (form.value.min_stock === '' || form.value.min_stock === null || isNaN(minStockVal) || minStockVal < 1) {
    toastStore.push({
      title: 'Error de validación',
      description: 'El nivel mínimo de existencias (stock mínimo) debe ser mayor o igual a 1.',
      type: 'error'
    });
    return;
  }
  if (minStockVal > 100000) {
    toastStore.push({
      title: 'Error de validación',
      description: 'El nivel mínimo de existencias no puede superar las 100,000 unidades.',
      type: 'error'
    });
    return;
  }

  const stockInicialVal = Number(form.value.stock_inicial);
  let costoInicialVal = null;
  if (form.value.stock_inicial !== '' && form.value.stock_inicial !== null) {
    if (isNaN(stockInicialVal) || stockInicialVal < 0) {
      toastStore.push({
        title: 'Error de validación',
        description: 'El stock inicial no puede ser negativo.',
        type: 'error'
      });
      return;
    }
    if (stockInicialVal > 100000) {
      toastStore.push({
        title: 'Error de validación',
        description: 'El stock inicial no puede superar las 100,000 unidades.',
        type: 'error'
      });
      return;
    }

    if (stockInicialVal > 0) {
      costoInicialVal = Number(form.value.costo_inicial);
      if (form.value.costo_inicial === '' || form.value.costo_inicial === null || isNaN(costoInicialVal) || costoInicialVal <= 0) {
        toastStore.push({
          title: 'Error de validación',
          description: 'El costo unitario inicial es requerido y debe ser mayor a 0 cuando el stock inicial es mayor a 0.',
          type: 'error'
        });
        return;
      }
    }
  }

  loading.value = true;
  try {
    await appStore.addSupply({
      name: form.value.nombre,
      category: form.value.categoria,
      description: form.value.observaciones || '',
      min_stock: Number(form.value.min_stock),
      initial_stock: stockInicialVal || 0,
      acquisition_cost: costoInicialVal,
    });

    toastStore.push({
      title: 'Insumo registrado',
      description: `${form.value.nombre} fue agregado al catálogo maestro con ${Number(form.value.stock_inicial) || 0} unidades iniciales.`,
      type: 'success',
    });

    resetForm();
  } catch (err) {
    console.error(err);
    const detail = err.response?.data?.detail || err.response?.data?.name?.[0] || err.response?.data?.sku?.[0] || 'Hubo un error al registrar el insumo.';
    toastStore.push({ title: 'Error al registrar', description: detail, type: 'error' });
  } finally {
    loading.value = false;
  }
}

</script>

<template>
  <div class="stack">
    <PageHeader
      title="Registrar insumo"
      subtitle="Alta de productos en el catálogo maestro de la clínica."
    />
    <DashboardCard title="Nuevo insumo" icon="notebook-pen">
      <form v-show="open" class="stack form-section" @submit.prevent="handleSubmit">
        <div class="field">
          <label for="nombre">Nombre*</label>
          <input
            class="input"
            id="nombre"
            v-model="form.nombre"
            required
            placeholder="Nombre del medicamento o insumo"
          />
        </div>
        <div class="field">
          <label for="categoria">Categoría*</label>
          <select class="select" id="categoria" v-model="form.categoria" required>
            <option value="" disabled>Seleccionar...</option>
            <option v-for="cat in CATEGORY_OPTIONS" :key="cat.value" :value="cat.value">
              {{ cat.label }}
            </option>
          </select>
        </div>
        <div class="field">
          <label for="min_stock">Nivel mínimo de existencias*</label>
          <input
            class="input"
            id="min_stock"
            v-model="form.min_stock"
            type="number"
            min="1"
            max="100000"
            required
            placeholder="Ejemplo: 10"
            @keypress="preventNegative"
            @input="sanitizeMinStock"
            @blur="sanitizeMinStock"
          />
        </div>
        <div class="field">
          <label for="stock_inicial">Stock inicial (Existencia disponible)</label>
          <input
            class="input"
            id="stock_inicial"
            v-model.number="form.stock_inicial"
            type="number"
            min="0"
            max="100000"
            placeholder="Ejemplo: 30"
            @keypress="preventNegative"
            @input="sanitizeStockInicial"
            @blur="sanitizeStockInicial"
          />
        </div>
        <div class="field" v-if="form.stock_inicial > 0">
          <label for="costo_inicial">Costo unitario inicial*</label>
          <input
            class="input"
            id="costo_inicial"
            v-model.number="form.costo_inicial"
            type="number"
            step="0.01"
            min="0.01"
            required
            placeholder="Ejemplo: 1.50"
            @keypress="preventNegative"
          />
        </div>
        <div class="field">
          <label for="observaciones">Descripción / Observaciones</label>
          <textarea
            class="textarea"
            id="observaciones"
            v-model="form.observaciones"
            placeholder="Notas internas del catálogo"
          />
        </div>
        <button class="btn btn--primary" type="submit" :disabled="loading">
          {{ loading ? 'Registrando...' : 'Registrar' }}
        </button>
      </form>
    </DashboardCard>
  </div>
</template>

<style scoped>
.form-section {
  margin-top: 28px;
}
</style>
