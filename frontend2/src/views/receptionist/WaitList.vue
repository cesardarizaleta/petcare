<script setup>
  import { onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';

  const appStore = useAppStore();
  const toastStore = useToastStore();

  onMounted(async () => {
    await appStore.fetchWaitingList();
  });

  async function callNext(entry) {
    try {
      await appStore.callNextPatient(entry.id);
      toastStore.push({
        title: 'Paciente llamado',
        description: `${entry.patientName} pasó a consulta.`,
        type: 'info',
      });
    } catch (e) {
      toastStore.push({ title: 'Error al llamar paciente', type: 'error' });
    }
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Lista de Espera"
      subtitle="Pacientes pendientes por atender dentro del turno actual."
    />

    <section class="card">
      <div class="list">
        <article
          v-for="entry in appStore.waitingList"
          :key="entry.id"
          class="list__item"
        >
          <div class="toolbar__group">
            <div class="list__item-main">
              <p class="list__title">{{ entry.patientName }}</p>
              <p class="list__subtitle">
                Propietario: {{ entry.ownerName }} · Prioridad: {{ entry.priority }}
              </p>
            </div>
          </div>
          <div class="toolbar__group">
            <StatusBadge :status="entry.status === 'WAITING' ? 'waiting' : 'in_progress'" />
            <button
              v-if="entry.status === 'WAITING'"
              class="btn btn--soft"
              type="button"
              @click="callNext(entry)"
            >
              Llamar
            </button>
            <span v-else class="chip chip--sage">En atención</span>
          </div>
        </article>
        <p v-if="!appStore.waitingList.length" class="muted">No hay pacientes en espera.</p>
      </div>
    </section>
  </div>
</template>
