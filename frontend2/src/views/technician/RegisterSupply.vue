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
  umbral: '',
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

async function handleSubmit() {
  if (form.value.umbral === '' || form.value.umbral === null || Number(form.value.umbral) < 1) {
    toastStore.push({
      title: 'Error de validación',
      description: 'El nivel mínimo de existencias (stock mínimo) debe ser mayor o igual a 1.',
      type: 'error'
    });
    return;
  }

  loading.value = true;
  try {
    await appStore.addSupply({
      name: form.value.nombre,
      category: form.value.categoria,
      description: form.value.observaciones || '',
      min_stock: Number(form.value.umbral),
    });

    toastStore.push({
      title: 'Insumo registrado',
      description: `${form.value.nombre} fue agregado al catálogo maestro.`,
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
          <label for="umbral">Nivel mínimo de existencias*</label>
          <input
            class="input"
            id="umbral"
            v-model="form.umbral"
            type="number"
            min="1"
            required
            placeholder="Ejemplo: 10"
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
