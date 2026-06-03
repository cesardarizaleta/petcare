<script setup>
  import { onMounted, reactive } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { extractApiError } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const callingIds = reactive({});

  onMounted(async () => {
    await appStore.fetchWaitingList();
  });

  async function callNext(entry) {
    callingIds[entry.id] = true;
    try {
      await appStore.callNextPatient(entry.id);
      toastStore.push({
        title: 'Paciente llamado',
        description: `${entry.patientName} pasó a consulta.`,
        type: 'info',
      });
    } catch (e) {
      toastStore.push({ title: 'Error al llamar paciente', description: extractApiError(e), type: 'error' });
    } finally {
      delete callingIds[entry.id];
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
                Propietario: 
                <router-link 
                  v-slot="{ navigate }" 
                  v-if="entry.ownerId" 
                  :to="`/reception/owners?id=${entry.ownerId}`" 
                  custom
                >
                  <span class="owner-link" @click="navigate" role="link">
                    {{ entry.ownerName }}
                  </span>
                </router-link>
                <span v-else>{{ entry.ownerName }}</span>
                · Prioridad: {{ entry.priority }}
              </p>
            </div>
          </div>
          <div class="toolbar__group">
            <StatusBadge :status="entry.status === 'WAITING' ? 'waiting' : 'in_progress'" />
            <button
              v-if="entry.status === 'WAITING'"
              class="btn btn--soft"
              type="button"
              :disabled="!!callingIds[entry.id]"
              @click="callNext(entry)"
            >
              {{ callingIds[entry.id] ? 'Llamando...' : 'Llamar' }}
            </button>
            <span v-else class="chip chip--sage">En atención</span>
          </div>
        </article>
        <p v-if="!appStore.waitingList.length" class="muted">No hay pacientes en espera.</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
  .owner-link {
    color: var(--brand-strong);
    font-weight: 700;
    text-decoration: underline;
    cursor: pointer;
    transition: color 0.16s ease;
  }
  .owner-link:hover {
    color: var(--brand);
  }
</style>
