<script setup>
  import { computed, ref, reactive, onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import PetAvatar from '@/components/shared/PetAvatar.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { formatDate, getOwnerAppointments, getOwnerPets, getPet, extractApiError } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const route = useRoute();

  const selectedOwnerId = ref('');
  const query = ref('');
  const isEditing = ref(false);
  const saving = ref(false);

  const editForm = reactive({
    name: '',
    dni: '',
    phone: '',
    address: '',
  });

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchOwners(),
        appStore.fetchPets(),
        appStore.fetchAppointments(),
      ]);
      const queryId = route.query.id;
      if (queryId) {
        const found = appStore.owners.find(o => o.id === queryId);
        if (found) {
          selectedOwnerId.value = queryId;
          // Clear query params dynamically to keep url clean
          window.history.replaceState({}, '', route.path);
        }
      }
    } catch (err) {
      console.error('Error fetching OwnersSearch data:', err);
    }
  });

  const filteredOwners = computed(() =>
    appStore.owners.filter((owner) => {
      const search = query.value.trim().toLowerCase();
      return (
        !search ||
        [owner.name, owner.email, owner.phone, owner.address].some((value) =>
          (value || '').toLowerCase().includes(search)
        )
      );
    })
  );

  const selectedOwner = computed(() => {
    if (selectedOwnerId.value) {
      return appStore.owners.find(o => o.id === selectedOwnerId.value) || null;
    }
    return filteredOwners.value[0] || appStore.owners[0] || null;
  });

  function selectOwner(owner) {
    selectedOwnerId.value = owner.id;
    isEditing.value = false;
  }

  function startEdit() {
    if (!selectedOwner.value) return;
    editForm.name = selectedOwner.value.name;
    editForm.dni = selectedOwner.value.dni || '';
    editForm.phone = selectedOwner.value.phone || '';
    editForm.address = selectedOwner.value.address || '';
    isEditing.value = true;
  }

  function cancelEdit() {
    isEditing.value = false;
  }

  async function saveOwner() {
    if (!editForm.name.trim()) {
      toastStore.push({ title: 'El nombre es obligatorio.', type: 'error' });
      return;
    }

    if (editForm.dni && !/^[0-9]{6,10}$/.test(editForm.dni)) {
      toastStore.push({
        title: 'Cédula / DNI inválido',
        description: 'La cédula debe contener entre 6 y 10 dígitos numéricos positivos.',
        type: 'error'
      });
      return;
    }

    if (editForm.phone && !/^\+?[\d\s\-()]{7,20}$/.test(editForm.phone)) {
      toastStore.push({
        title: 'Teléfono inválido',
        description: 'El teléfono debe tener un formato válido (entre 7 y 20 caracteres, permitiendo números, espacios, guiones y paréntesis).',
        type: 'error'
      });
      return;
    }

    saving.value = true;
    try {
      await appStore.updateOwnerById(selectedOwner.value.id, editForm);
      toastStore.push({
        title: 'Propietario actualizado',
        description: 'Los cambios fueron guardados correctamente.',
        type: 'success',
      });
      isEditing.value = false;
    } catch (err) {
      toastStore.push({
        title: 'Error al actualizar propietario',
        description: extractApiError(err),
        type: 'error',
      });
    } finally {
      saving.value = false;
    }
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Propietarios"
      subtitle="Búsqueda, consulta cruzada y edición de datos de dueños."
    />

    <section class="input-row">
      <input
        v-model="query"
        class="input"
        type="search"
        placeholder="Buscar por nombre, correo, teléfono o dirección..."
      />
    </section>

    <section class="split">
      <div class="card">
        <div class="list">
          <article
            v-for="owner in filteredOwners"
            :key="owner.id"
            class="list__item list__item--clickable"
            :class="{ 'list__item--active': selectedOwner && selectedOwner.id === owner.id }"
            @click="selectOwner(owner)"
          >
            <div class="list__item-main">
              <p class="list__title">{{ owner.name }}</p>
              <p class="list__subtitle">{{ owner.email }} · {{ owner.phone || '—' }}</p>
            </div>
            <span class="chip chip--brand"
              >{{ getOwnerPets(appStore.pets, owner.id).length }} mascotas</span
            >
          </article>
          <p v-if="!filteredOwners.length" class="muted" style="padding: 12px 4px;">
            No se encontraron propietarios.
          </p>
        </div>
      </div>

      <div class="card" v-if="selectedOwner">
        <!-- DETALLES VISTA DE LECTURA -->
        <div v-if="!isEditing" class="stack">
          <div class="toolbar-header">
            <div>
              <h2 class="section__title" style="margin: 0;">{{ selectedOwner.name }}</h2>
              <p class="muted" style="margin-top: 4px; font-size: 0.9rem;">
                DNI / Cédula: <strong>{{ selectedOwner.dni || '—' }}</strong>
              </p>
            </div>
            <button class="btn btn--soft" type="button" @click="startEdit">
              Editar Datos
            </button>
          </div>

          <div class="owner-summary-grid">
            <div class="card card--stat">
              <p class="eyebrow" style="margin-bottom: 4px;">Teléfono</p>
              <strong>{{ selectedOwner.phone || '—' }}</strong>
            </div>
            <div class="card card--stat">
              <p class="eyebrow" style="margin-bottom: 4px;">Correo</p>
              <strong style="word-break: break-all; font-size: 0.88rem;">{{ selectedOwner.email }}</strong>
            </div>
            <div class="card card--stat" style="grid-column: span 2;">
              <p class="eyebrow" style="margin-bottom: 4px;">Dirección</p>
              <strong>{{ selectedOwner.address || '—' }}</strong>
            </div>
          </div>

          <div class="section-divider">
            <h3 class="eyebrow" style="margin-bottom: 12px;">Mascotas</h3>
            <div class="list" style="gap: 8px; margin-bottom: 20px;">
              <article
                v-for="pet in getOwnerPets(appStore.pets, selectedOwner.id)"
                :key="pet.id"
                class="list__item"
                style="padding: 10px 14px;"
              >
                <div class="toolbar__group">
                  <PetAvatar :pet="pet" size="sm" />
                  <div class="list__item-main">
                    <p class="list__title" style="font-size: 0.95rem;">{{ pet.name }}</p>
                    <p class="list__subtitle" style="font-size: 0.82rem;">{{ pet.breed }} ({{ pet.species }})</p>
                  </div>
                </div>
              </article>
              <p v-if="!getOwnerPets(appStore.pets, selectedOwner.id).length" class="muted" style="font-size: 0.88rem; padding: 4px;">
                No tiene mascotas registradas.
              </p>
            </div>

            <h3 class="eyebrow" style="margin-bottom: 12px;">Últimas citas</h3>
            <div class="list" style="gap: 8px;">
              <article
                v-for="appointment in getOwnerAppointments(
                  appStore.appointments,
                  selectedOwner.id
                ).slice(0, 3)"
                :key="appointment.id"
                class="list__item"
                style="padding: 10px 14px;"
              >
                <div class="list__item-main">
                  <p class="list__title" style="font-size: 0.92rem;">{{ formatDate(appointment.date) }} · {{ appointment.time }}</p>
                  <p class="list__subtitle" style="font-size: 0.82rem;">
                    {{ appointment.reason }} · {{ getPet(appStore.pets, appointment.petId)?.name }}
                  </p>
                </div>
                <StatusBadge :status="appointment.status" />
              </article>
              <p v-if="!getOwnerAppointments(appStore.appointments, selectedOwner.id).length" class="muted" style="font-size: 0.88rem; padding: 4px;">
                No tiene citas registradas.
              </p>
            </div>
          </div>
        </div>

        <!-- MODO DE EDICIÓN -->
        <div v-else class="stack">
          <h2 class="section__title">Editar Propietario</h2>
          <p class="muted" style="margin-bottom: 18px;">Modifica los campos del propietario y guarda los cambios.</p>

          <form @submit.prevent="saveOwner" class="input-row">
            <label class="field">
              <span>Nombre y Apellido *</span>
              <input v-model="editForm.name" class="input" type="text" required placeholder="Nombre completo" />
            </label>

            <div class="input-grid">
              <label class="field">
                <span>DNI / Cédula</span>
                <input v-model="editForm.dni" class="input" type="text" placeholder="Ej: 12345678" />
              </label>
              <label class="field">
                <span>Teléfono</span>
                <input v-model="editForm.phone" class="input" type="tel" placeholder="Número telefónico" />
              </label>
            </div>

            <label class="field">
              <span>Dirección</span>
              <textarea v-model="editForm.address" class="textarea" rows="3" placeholder="Dirección de residencia"></textarea>
            </label>

            <div class="toolbar" style="justify-content: flex-end; gap: 12px; margin-top: 14px; display: flex; flex-wrap: wrap;">
              <button class="btn btn--ghost" type="button" @click="cancelEdit" :disabled="saving">
                Cancelar
              </button>
              <button class="btn btn--primary" type="submit" :disabled="saving">
                {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
  .list__item--clickable {
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s, transform 0.2s;
  }
  .list__item--clickable:hover {
    background: rgba(194, 167, 105, 0.06);
    transform: translateY(-1px);
  }
  .list__item--active {
    background: rgba(194, 167, 105, 0.12) !important;
    border-color: rgba(194, 167, 105, 0.45) !important;
    box-shadow: 0 4px 12px rgba(194, 167, 105, 0.05);
  }
  .toolbar-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 12px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 14px;
    margin-bottom: 14px;
  }
  .card--stat {
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 12px;
  }
  .section-divider {
    border-top: 1px solid var(--border);
    padding-top: 16px;
  }

  .owner-summary-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 18px;
    margin-bottom: 22px;
  }

  .select,
  .input,
  .textarea {
    max-width: 100%;
  }

  .list__item-main {
    min-width: 0;
    flex: 1;
  }

  .list__title,
  .list__subtitle {
    overflow-wrap: anywhere;
    word-break: break-word;
  }

  @media (max-width: 600px) {
    .owner-summary-grid {
      grid-template-columns: 1fr;
    }
    .owner-summary-grid > div {
      grid-column: span 1 !important;
    }
  }

  @media (max-width: 480px) {
    .list__item {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }
    .list__item > .chip,
    .list__item > :deep(.status-badge) {
      align-self: flex-start;
      margin-top: 4px;
    }
  }
</style>
