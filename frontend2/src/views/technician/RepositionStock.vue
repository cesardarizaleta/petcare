<script setup>
import { ref, computed } from 'vue';
import PageHeader from '@/components/shared/PageHeader.vue';
import DashboardCard from '@/components/shared/DashboardCard.vue';
import { useAppStore } from '@/stores/useAppStore';
import { useToastStore } from '@/stores/useToastStore';

const EMPTY_FORM = {
  insumoId: '',
  quantity: 1,
  batch: '',
  expirationDate: '',
  observations: '',
};

const appStore = useAppStore();
const toastStore = useToastStore();

const today = new Date().toISOString().split('T')[0];
const open = ref(true);
const form = ref({ ...EMPTY_FORM });

const listaInsumos = computed(() => appStore.inventory);

const resetForm = () => {
  Object.assign(form.value, EMPTY_FORM);
};

const guardarEntrada = async () => {
  if (!form.value.insumoId || !form.value.batch || !form.value.expirationDate) {
    toastStore.push({
      title: 'Complete los campos obligatorios',
      description: 'Insumo, lote y fecha de vencimiento son requeridos.',
      type: 'error',
    });
    return;
  }

  if (form.value.quantity <= 0) {
    toastStore.push({
      title: 'Cantidad inválida',
      description: 'La cantidad recibida debe ser un número positivo.',
      type: 'error',
    });
    return;
  }

  try {
    await appStore.addBatch(form.value.insumoId, {
      batch: form.value.batch,
      expirationDate: form.value.expirationDate,
      quantity: form.value.quantity,
    });

    const insumo = listaInsumos.value.find((item) => item.id === form.value.insumoId);

    toastStore.push({
      title: 'Reposición registrada',
      description: insumo
        ? `Lote registrado exitosamente para ${insumo.name}.`
        : 'Entrada de mercancía guardada.',
      type: 'success',
    });

    resetForm();
  } catch (error) {
    console.error(error);
    const detail = error.response?.data?.error || error.response?.data?.detail || 'Hubo un error al registrar el lote en el servidor.';
    toastStore.push({
      title: 'Error al registrar lote',
      description: detail,
      type: 'error',
    });
  }
};
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Reposición de Stock"
      subtitle="Registro de entrada de mercancía por lote."
    />

    <DashboardCard title="Entrada por lote" icon="notebook-pen">
      <form v-show="open" class="stack form-section" @submit.prevent="guardarEntrada">
        <div class="field">
          <label for="insumo">Seleccionar insumo del catálogo*</label>
          <select id="insumo" v-model="form.insumoId" class="select" required>
            <option value="" disabled>Seleccione un insumo del catálogo...</option>
            <option v-for="insumo in listaInsumos" :key="insumo.id" :value="insumo.id">
              {{ insumo.name }} (Stock actual: {{ insumo.quantity }} uds.)
            </option>
          </select>
        </div>

        <div class="field">
          <label for="cant">Cantidad recibida*</label>
          <input
            class="input"
            id="cant"
            v-model.number="form.quantity"
            type="number"
            min="1"
            required
            placeholder="1"
          />
        </div>

        <div class="field">
          <label for="lote">Número de lote*</label>
          <input
            id="lote"
            type="text"
            class="input"
            v-model="form.batch"
            placeholder="Ej: LOT-2026-AF"
            required
          />
        </div>

        <div class="field">
          <label for="caducidad">Fecha de vencimiento*</label>
          <input
            id="caducidad"
            type="date"
            class="input"
            v-model="form.expirationDate"
            :min="today"
            required
          />
        </div>

        <div class="field">
          <label for="observaciones">Observaciones</label>
          <textarea
            class="textarea"
            id="observaciones"
            v-model="form.observations"
            placeholder="Estado del empaque, temperatura, etc."
          />
        </div>

        <button class="btn btn--primary" type="submit">Registrar entrada</button>
      </form>
    </DashboardCard>
  </div>
</template>

<style scoped>
.form-section {
  margin-top: 28px;
}
</style>
