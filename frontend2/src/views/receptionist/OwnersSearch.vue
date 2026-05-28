<script setup>
  import { computed, ref, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { formatDate, getOwnerAppointments, getOwnerPets, getPet } from '@/lib/petcare';

  const appStore = useAppStore();

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchOwners(),
        appStore.fetchPets(),
        appStore.fetchAppointments(),
      ]);
    } catch (err) {
      console.error('Error fetching OwnersSearch data:', err);
    }
  });

  const query = ref('');

  const filteredOwners = computed(() =>
    appStore.owners.filter((owner) => {
      const search = query.value.trim().toLowerCase();
      return (
        !search ||
        [owner.name, owner.email, owner.phone, owner.address].some((value) =>
          value.toLowerCase().includes(search)
        )
      );
    })
  );

  const selectedOwner = computed(() => filteredOwners.value[0] || appStore.owners[0] || null);
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Propietarios"
      subtitle="Búsqueda y consulta cruzada de dueños, mascotas y citas."
    />

    <section class="input-row">
      <input
        v-model="query"
        class="input"
        type="search"
        placeholder="Buscar por nombre, correo, teléfono o dirección"
      />
    </section>

    <section class="split">
      <div class="card">
        <div class="list">
          <article v-for="owner in filteredOwners" :key="owner.id" class="list__item">
            <div class="list__item-main">
              <p class="list__title">{{ owner.name }}</p>
              <p class="list__subtitle">{{ owner.email }} · {{ owner.phone }}</p>
            </div>
            <span class="chip chip--brand"
              >{{ getOwnerPets(appStore.pets, owner.id).length }} mascotas</span
            >
          </article>
        </div>
      </div>

      <div class="card" v-if="selectedOwner">
        <h2 class="section__title">{{ selectedOwner.name }}</h2>
        <p class="muted">{{ selectedOwner.address }}</p>
        <div class="section" style="margin-top: 18px">
          <h3 class="eyebrow">Mascotas</h3>
          <article
            v-for="pet in getOwnerPets(appStore.pets, selectedOwner.id)"
            :key="pet.id"
            class="list__item"
          >
            <div class="toolbar__group">
              <PetAvatar :pet="pet" size="sm" />
              <div class="list__item-main">
                <p class="list__title">{{ pet.name }}</p>
                <p class="list__subtitle">{{ pet.breed }}</p>
              </div>
            </div>
          </article>
          <h3 class="eyebrow">Últimas citas</h3>
          <article
            v-for="appointment in getOwnerAppointments(
              appStore.appointments,
              selectedOwner.id
            ).slice(0, 3)"
            :key="appointment.id"
            class="list__item"
          >
            <div class="list__item-main">
              <p class="list__title">{{ formatDate(appointment.date) }} · {{ appointment.time }}</p>
              <p class="list__subtitle">
                {{ appointment.reason }} · {{ getPet(appStore.pets, appointment.petId)?.name }}
              </p>
            </div>
            <StatusBadge :status="appointment.status" />
          </article>
        </div>
      </div>
    </section>
  </div>
</template>
