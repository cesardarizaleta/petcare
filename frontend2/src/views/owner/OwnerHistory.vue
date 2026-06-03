<script setup>
  import { computed, onMounted, ref } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import {
    formatDate,
    getLatestConsultation,
    getLatestDeworming,
    getLatestVaccine,
    getOwnerPets,
  } from '@/lib/petcare';

  const appStore = useAppStore();
  const loading = ref(false);
  const loadedConsultations = ref([]);
  const loadedVaccines = ref([]);
  const loadedDewormings = ref([]);

  onMounted(async () => {
    loading.value = true;
    try {
      await Promise.all([
        appStore.fetchProfile(),
        appStore.fetchPets(),
        appStore.fetchAppointments(),
      ]);

      // Fetch medical records and vaccination plans for all of the owner's pets
      const petsList = getOwnerPets(appStore.pets, appStore.currentUserId);
      
      const petPromises = petsList.flatMap(pet => [
        appStore.fetchMedicalRecord(pet.id).then(record => {
          const mapped = (record.consultations || []).map(c => ({
            ...c,
            id: c.id || `c-${Date.now()}-${Math.random()}`,
            petId: pet.id,
            petName: pet.name
          }));
          loadedConsultations.value.push(...mapped);
        }),
        appStore.fetchVaccinationSchedule(pet.id).then(schedule => {
          const mappedVaccines = schedule.filter(e => e.event_type === 'VACCINE').map(v => ({
            id: v.id || `v-${Date.now()}-${Math.random()}`,
            petId: pet.id,
            petName: pet.name,
            name: v.vaccine_name || 'Vacuna',
            nextDate: v.next_due_date,
            lot: v.sanitary_batch || '—'
          }));
          const mappedDewormings = schedule.filter(e => e.event_type === 'DEWORMING').map(d => ({
            id: d.id || `d-${Date.now()}-${Math.random()}`,
            petId: pet.id,
            petName: pet.name,
            product: d.vaccine_name || 'Desparasitante',
            nextDate: d.next_due_date,
            weight: d.dose || '—'
          }));
          loadedVaccines.value.push(...mappedVaccines);
          loadedDewormings.value.push(...mappedDewormings);
        })
      ]);
      await Promise.all(petPromises);
    } catch (err) {
      console.error('Error fetching owner history data:', err);
    } finally {
      loading.value = false;
    }
  });

  const pets = computed(() => getOwnerPets(appStore.pets, appStore.currentUserId));
  
  const consultations = computed(() =>
    [...loadedConsultations.value].sort((a, b) => (b.date || '').localeCompare(a.date || ''))
  );
  
  const vaccines = computed(() =>
    [...loadedVaccines.value].sort((a, b) => (b.nextDate || '').localeCompare(a.nextDate || ''))
  );
  
  const dewormings = computed(() =>
    [...loadedDewormings.value].sort((a, b) => (b.nextDate || '').localeCompare(a.nextDate || ''))
  );
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Historial"
      subtitle="Consultas, vacunas y tratamientos anteriores del propietario."
    />

    <section class="grid grid--3">
      <DashboardCard title="Consultas" icon="stethoscope">
        <div class="list">
          <p v-if="loading" class="muted" style="padding: 1rem;">Cargando consultas...</p>
          <template v-else>
            <article v-for="item in consultations" :key="item.id" class="list__item">
              <div class="list__item-main">
                <p class="list__title">
                  {{ formatDate(item.date) }} 
                  <span class="muted" style="font-size: 0.8rem;">· {{ item.petName }}</span>
                </p>
                <p class="list__subtitle">{{ item.diagnosis }}</p>
              </div>
              <StatusBadge status="completed" />
            </article>
            <p v-if="!consultations.length" class="muted" style="padding: 1rem;">Sin consultas registradas.</p>
          </template>
        </div>
      </DashboardCard>

      <DashboardCard title="Vacunas" icon="syringe">
        <div class="list">
          <p v-if="loading" class="muted" style="padding: 1rem;">Cargando vacunas...</p>
          <template v-else>
            <article v-for="item in vaccines" :key="item.id" class="list__item">
              <div class="list__item-main">
                <p class="list__title">
                  {{ item.name }} 
                  <span class="muted" style="font-size: 0.8rem;">· {{ item.petName }}</span>
                </p>
                <p class="list__subtitle">Próxima: {{ formatDate(item.nextDate) }}</p>
              </div>
              <span class="chip chip--sage">{{ item.lot }}</span>
            </article>
            <p v-if="!vaccines.length" class="muted" style="padding: 1rem;">Sin vacunas registradas.</p>
          </template>
        </div>
      </DashboardCard>

      <DashboardCard title="Desparasitaciones" icon="worm">
        <div class="list">
          <p v-if="loading" class="muted" style="padding: 1rem;">Cargando desparasitaciones...</p>
          <template v-else>
            <article v-for="item in dewormings" :key="item.id" class="list__item">
              <div class="list__item-main">
                <p class="list__title">
                  {{ item.product }} 
                  <span class="muted" style="font-size: 0.8rem;">· {{ item.petName }}</span>
                </p>
                <p class="list__subtitle">Próxima: {{ formatDate(item.nextDate) }}</p>
              </div>
              <span class="chip chip--cream">{{ item.weight }}</span>
            </article>
            <p v-if="!dewormings.length" class="muted" style="padding: 1rem;">Sin desparasitaciones registradas.</p>
          </template>
        </div>
      </DashboardCard>
    </section>

    <section class="card">
      <div class="toolbar">
        <h2 class="section__title">Mascotas con seguimiento</h2>
      </div>
      
      <p v-if="loading" class="muted" style="padding: 2rem; text-align: center;">Cargando mascotas...</p>
      
      <div v-else class="list" style="margin-top: 16px">
        <article v-for="pet in pets" :key="pet.id" class="list__item">
          <div class="toolbar__group">
            <PetAvatar :pet="pet" size="sm" />
            <div class="list__item-main">
              <p class="list__title">{{ pet.name }}</p>
              <p class="list__subtitle">{{ pet.breed }} · {{ pet.color }}</p>
            </div>
          </div>
          <div class="toolbar__group">
            <span class="chip chip--brand"
              >Consulta:
              {{
                getLatestConsultation(appStore.consultations, pet.id)?.date
                  ? formatDate(getLatestConsultation(appStore.consultations, pet.id).date)
                  : 'Sin datos'
              }}</span
            >
            <span class="chip chip--sage"
              >Vacuna:
              {{
                getLatestVaccine(appStore.vaccines, pet.id)?.date
                  ? formatDate(getLatestVaccine(appStore.vaccines, pet.id).date)
                  : 'Sin datos'
              }}</span
            >
            <span class="chip chip--cream"
              >Desparasitación:
              {{
                getLatestDeworming(appStore.dewormings, pet.id)?.date
                  ? formatDate(getLatestDeworming(appStore.dewormings, pet.id).date)
                  : 'Sin datos'
              }}</span
            >
          </div>
        </article>
        <p v-if="!pets.length" class="muted" style="padding: 1rem;">No tienes mascotas registradas.</p>
      </div>
    </section>
  </div>
</template>
