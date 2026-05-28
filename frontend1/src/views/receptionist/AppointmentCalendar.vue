<script setup>
  import { computed, ref, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import {
    formatDate,
    getAppointmentsByDate,
    getPet,
    getVet,
    daysFromNow,
    sortAppointments,
    timeSlots,
  } from '@/lib/petcare';

  const appStore = useAppStore();
  const showEmptySlots = ref(true);

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchPets(),
        appStore.fetchAppointments()
      ]);
    } catch (err) {
      console.error('Error loading calendar data:', err);
    }
  });

  const dates = computed(() =>
    Array.from({ length: 5 }, (_, index) => {
      const date = daysFromNow(index);
      const dayAppointments = getAppointmentsByDate(appStore.appointments, date);
      
      const vetsSchedule = appStore.vets.map(vet => {
        const vetAppointments = dayAppointments.filter(a => a.vetId === vet.id);
        const slots = timeSlots.map(time => {
          const appointment = vetAppointments.find(a => a.time === time);
          return { time, appointment };
        });
        return { vet, slots };
      });

      return { date, vetsSchedule };
    })
  );
</script>

<template>
  <div class="stack">
    <PageHeader title="Calendario" subtitle="Vista de agenda y distribución de citas por fecha." />

    <div class="toolbar" style="margin-bottom: 1rem;">
      <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
        <input type="checkbox" v-model="showEmptySlots" />
        <span style="font-weight: 500;">Mostrar huecos disponibles</span>
      </label>
    </div>

    <section class="grid grid--2">
      <DashboardCard
        v-for="day in dates"
        :key="day.date"
        :title="formatDate(day.date)"
        icon="calendar-days"
      >
   <div class="stack" style="gap: 1.5rem">
          <div v-for="vetSchedule in day.vetsSchedule" :key="vetSchedule.vet.id">
            <h4 style="margin-bottom: 0.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.25rem;">
              {{ vetSchedule.vet.name }}
            </h4>
            <div class="list">
              <article
                v-for="slot in vetSchedule.slots"
                :key="slot.time"
                class="list__item"
                style="padding: 0.5rem;"
                v-show="slot.appointment || showEmptySlots"
              >
                <div class="toolbar__group">
                  <span style="font-weight: 500; min-width: 3rem;">{{ slot.time }}</span>
                  <template v-if="slot.appointment">
                    <PetAvatar :pet="getPet(appStore.pets, slot.appointment.petId)" size="sm" />
                    <div class="list__item-main">
                      <p class="list__title">
                        {{ getPet(appStore.pets, slot.appointment.petId)?.name }}
                        <span v-if="slot.appointment.type === 'Emergencia'" class="chip chip--danger" style="margin-left: 8px; padding: 0.2rem 0.5rem; font-size: 0.7rem;">
                          Emergencia ({{ slot.appointment.priority }})
                        </span>
                      </p>
                      <p class="list__subtitle">{{ slot.appointment.reason }}</p>
                    </div>
                  </template>
                  <template v-else>
                    <span class="muted" style="font-size: 0.85rem">Disponible</span>
                  </template>
                </div>
                <StatusBadge v-if="slot.appointment" :status="slot.appointment.status" />
              </article>
            </div>
          </div>
        </div>
      </DashboardCard>
    </section>
  </div>
</template>
