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

const resetForm = () => {
  Object.assign(form.value, EMPTY_FORM);
};

function handleSubmit() {
  appStore.addSupply({
    id: Date.now(),
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
        <button class="btn btn--primary" type="submit">Registrar</button>
      </form>
    </DashboardCard>
  </div>
</template>

<style scoped>
.form-section {
  margin-top: 28px;
}
</style>
