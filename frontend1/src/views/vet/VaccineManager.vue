<script setup>
  import { computed, reactive, onMounted, watch } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { formatDate, getTodayShortDate } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const form = reactive({
    petId: '',
    name: '',
    date: getTodayShortDate(),
    nextDate: '2026-06-08',
    lot: '',
    notes: '',
  });

  onMounted(async () => {
    try {
      await appStore.fetchPets();
    } catch (err) {
      console.error('Error loading vaccine manager pets:', err);
    }
  });

  watch(
    () => appStore.pets,
    (pets) => {
      if (pets.length && !form.petId) {
        form.petId = pets[0].id;
      }
    },
    { immediate: true, deep: true }
  );

  const vaccines = computed(() =>
    appStore.vaccines.slice().sort((left, right) => `${right.date}`.localeCompare(left.date))
  );

  function saveVaccine() {
    if (!form.petId || !form.name || !form.date || !form.nextDate) {
      toastStore.push({ title: 'Completa la vacuna', type: 'error' });
      return;
    }

    appStore.addVaccine({
      id: `vac${Date.now()}`,
      petId: form.petId,
      name: form.name,
      date: form.date,
      nextDate: form.nextDate,
      appliedBy: appStore.currentUserId || 'v1',
      lot: form.lot,
      notes: form.notes,
    });

    toastStore.push({
      title: 'Vacuna guardada',
      description: 'El registro de vacunación fue agregado.',
      type: 'success',
    });
  }
</script>

<template>
  <div class="stack">
    <PageHeader title="Vacunas" subtitle="Gestión y programación de vacunas por mascota." />

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
          <div class="input-grid">
            <label class="field"
              ><span>Nombre</span
              ><input v-model="form.name" class="input" type="text" placeholder="Séxtuple"
            /></label>
            <label class="field"
              ><span>Lote</span><input v-model="form.lot" class="input" type="text"
            /></label>
          </div>
          <div class="input-grid">
            <label class="field"
              ><span>Fecha</span><input v-model="form.date" class="input" type="date"
            /></label>
            <label class="field"
              ><span>Próxima fecha</span><input v-model="form.nextDate" class="input" type="date"
            /></label>
          </div>
          <label class="field"
            ><span>Notas</span><textarea v-model="form.notes" class="textarea" rows="3" />
          </label>
          <button class="btn btn--primary" type="button" @click="saveVaccine">
            Guardar vacuna
          </button>
        </div>
      </section>

      <section class="card table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Mascota</th>
              <th>Vacuna</th>
              <th>Fecha</th>
              <th>Próxima</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in vaccines" :key="item.id" class="table__row">
              <td>{{ appStore.pets.find((pet) => pet.id === item.petId)?.name }}</td>
              <td>{{ item.name }}</td>
              <td>{{ formatDate(item.date) }}</td>
              <td>{{ formatDate(item.nextDate) }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </div>
</template>
