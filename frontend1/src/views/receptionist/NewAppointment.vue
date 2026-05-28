<script setup>
  import { computed, reactive, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { timeSlots, getTodayShortDate } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();

  const ownerId = reactive({ value: appStore.owners[0]?.id || '' });
  const form = reactive({
    ownerId: ownerId.value,
    petId: '',
    vetId: appStore.vets[0]?.id || 'v1',
    date: getTodayShortDate(),
    time: '09:00',
    type: 'Normal',
    priority: 'Media',
    reason: '',
    notes: '',
  });

  const ownerPets = computed(() => appStore.pets.filter((pet) => pet.ownerId === form.ownerId));

  watch(
    ownerPets,
    (pets) => {
      if (!pets.length) {
        form.petId = '';
        return;
      }
      if (!pets.some((pet) => pet.id === form.petId)) {
        form.petId = pets[0].id;
      }
    },
    { immediate: true }
  );

  function saveAppointment() {
    if (!form.ownerId || !form.petId || !form.reason) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
      return;
    }

    appStore.addAppointment({
      id: `a${Date.now()}`,
      ownerId: form.ownerId,
      petId: form.petId,
      vetId: form.vetId,
      date: form.date,
      time: form.time,
      type: form.type,
      priority: form.type === 'Emergencia' ? form.priority : null,
      reason: form.reason,
      status: 'scheduled',
      notes: form.notes,
    });

    toastStore.push({
      title: 'Cita creada',
      description: 'La cita fue guardada correctamente.',
      type: 'success',
    });
    router.push('/reception/dashboard');
  }
</script>

<template>
  <div class="stack">
    <PageHeader title="Nueva Cita" subtitle="Alta manual de citas para el equipo de recepción." />

    <section class="card">
      <div class="input-row">
        <div class="input-grid">
          <label class="field">
            <span>Propietario</span>
            <select v-model="form.ownerId" class="select">
              <option v-for="owner in appStore.owners" :key="owner.id" :value="owner.id">
                {{ owner.name }}
              </option>
            </select>
          </label>
          <label class="field">
            <span>Mascota</span>
            <select v-model="form.petId" class="select">
              <option v-for="pet in ownerPets" :key="pet.id" :value="pet.id">
                {{ pet.name }} · {{ pet.breed }}
              </option>
            </select>
          </label>
        </div>

        <div class="input-grid">
          <label class="field">
            <span>Veterinario</span>
            <select v-model="form.vetId" class="select">
              <option v-for="vet in appStore.vets" :key="vet.id" :value="vet.id">
                {{ vet.name }} · {{ vet.specialty }}
              </option>
            </select>
          </label>
          <label class="field">
            <span>Fecha</span>
            <input v-model="form.date" class="input" type="date" />
          </label>
        </div>

        <div class="input-grid">
          <label class="field">
            <span>Hora</span>
            <select v-model="form.time" class="select">
              <option v-for="slot in timeSlots" :key="slot" :value="slot">{{ slot }}</option>
            </select>
          </label>
          <label class="field">
            <span>Motivo</span>
            <input v-model="form.reason" class="input" type="text" placeholder="Control anual" />
          </label>
        </div>

        <div class="input-grid">
          <label class="field">
            <span>Tipo de consulta</span>
            <select v-model="form.type" class="select">
              <option value="Normal">Normal</option>
              <option value="Emergencia">Emergencia</option>
            </select>
          </label>
          <label class="field" v-if="form.type === 'Emergencia'">
            <span>Prioridad</span>
            <select v-model="form.priority" class="select">
              <option value="Baja">Baja</option>
              <option value="Media">Media</option>
              <option value="Alta">Alta</option>
              <option value="Crítica">Crítica</option>
            </select>
          </label>
        </div>

        <label class="field">
          <span>Notas</span>
          <textarea v-model="form.notes" class="textarea" rows="4" />
        </label>

        <button class="btn btn--primary" type="button" @click="saveAppointment">
          Guardar cita
        </button>
      </div>
    </section>
  </div>
</template>
