<script setup>
import { ref } from 'vue';
import PageHeader from '@/components/shared/PageHeader.vue';
import DashboardCard from '@/components/shared/DashboardCard.vue';
import { useAppStore } from '@/stores/useAppStore';
import { useToastStore } from '@/stores/useToastStore';

const EMPTY_FORM = {
  nombre: '',
  tipo: '',
  cantidad: '',
  precio: '',
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

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

async function handleSubmit() {
  if (form.value.cantidad !== '' && Number(form.value.cantidad) < 0) {
    toastStore.push({
      title: 'Error de validación',
      description: 'La cantidad disponible no puede ser negativa.',
      type: 'error'
    });
    return;
  }

  if (form.value.precio !== '' && Number(form.value.precio) < 0) {
    toastStore.push({
      title: 'Error de validación',
      description: 'El costo unitario no puede ser negativo.',
      type: 'error'
    });
    return;
  }

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
    // Simulated premium micro-delay for realistic API communication
    await new Promise((resolve) => setTimeout(resolve, 600));
    
    appStore.addSupply({
      id: generateUUID(),
      name: form.value.nombre,
      type: form.value.tipo,
      quantity: Number(form.value.cantidad),
      unitCost: Number(form.value.precio),
      umbral: Number(form.value.umbral),
      batches: [],
    });

    toastStore.push({
      title: 'Insumo registrado',
      description: `${form.value.nombre} fue agregado al catálogo maestro.`,
      type: 'success',
    });

    resetForm();
  } catch (err) {
    console.error(err);
    toastStore.push({ title: 'Error al registrar', type: 'error' });
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
          <label for="tipo">Tipo*</label>
          <select class="select" id="tipo" v-model="form.tipo" required>
            <option value="" disabled>Seleccionar...</option>
            <option>Medicamento</option>
            <option>Insumo</option>
          </select>
        </div>
        <div class="field">
          <label for="cantidad">Cantidad*</label>
          <input
            class="input"
            id="cantidad"
            v-model="form.cantidad"
            type="number"
            min="1"
            required
            placeholder="Cantidad disponible"
          />
        </div>
        <div class="field">
          <label for="precio">Costo unitario (USD)*</label>
          <input
            class="input"
            id="precio"
            v-model="form.precio"
            type="number"
            min="0"
            step="0.01"
            required
            placeholder="Costo por unidad"
          />
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
          <label for="observaciones">Observaciones</label>
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
