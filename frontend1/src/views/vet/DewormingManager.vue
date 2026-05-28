<script setup>
  import { computed, reactive } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { formatDate, getTodayShortDate } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const form = reactive({
    petId: appStore.pets[0]?.id || '',
    product: '',
    date: getTodayShortDate(),
    nextDate: '2026-06-08',
    weight: '',
    notes: '',
  });

  const dewormings = computed(() =>
    appStore.dewormings.slice().sort((left, right) => `${right.date}`.localeCompare(left.date))
  );

  function saveDeworming() {
    if (!form.petId || !form.product || !form.date || !form.nextDate) {
      toastStore.push({ title: 'Completa la desparasitación', type: 'error' });
      return;
    }

    appStore.addDeworming({
      id: `d${Date.now()}`,
      petId: form.petId,
      product: form.product,
      date: form.date,
      nextDate: form.nextDate,
      appliedBy: appStore.currentUserId || 'v1',
      weight: Number(form.weight) || 0,
      notes: form.notes,
    });

    toastStore.push({
      title: 'Desparasitación guardada',
      description: 'El registro fue agregado correctamente.',
      type: 'success',
    });
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Desparasitaciones"
      subtitle="Registro y seguimiento de desparasitaciones por paciente."
    />

    <section class="split">
      <section class="card">
        <div class="input-row">
          <label class="field"
            ><span>Mascota</span
            ><select v-model="form.petId" class="select">
              <option v-for="pet in appStore.pets" :key="pet.id" :value="pet.id">
                {{ pet.name }}
              </option>
            </select></label
          >
          <label class="field"
            ><span>Producto</span
            ><input v-model="form.product" class="input" type="text" placeholder="Milbemax"
          /></label>
          <div class="input-grid">
            <label class="field"
              ><span>Fecha</span><input v-model="form.date" class="input" type="date"
            /></label>
            <label class="field"
              ><span>Próxima fecha</span><input v-model="form.nextDate" class="input" type="date"
            /></label>
          </div>
          <div class="input-grid">
            <label class="field"
              ><span>Peso</span
              ><input v-model="form.weight" class="input" type="number" min="0" step="0.1"
            /></label>
            <label class="field"
              ><span>Notas</span><input v-model="form.notes" class="input" type="text"
            /></label>
          </div>
          <button class="btn btn--primary" type="button" @click="saveDeworming">
            Guardar desparasitación
          </button>
        </div>
      </section>

      <section class="card table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Mascota</th>
              <th>Producto</th>
              <th>Fecha</th>
              <th>Próxima</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in dewormings" :key="item.id" class="table__row">
              <td>{{ appStore.pets.find((pet) => pet.id === item.petId)?.name }}</td>
              <td>{{ item.product }}</td>
              <td>{{ formatDate(item.date) }}</td>
              <td>{{ formatDate(item.nextDate) }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </div>
</template>
