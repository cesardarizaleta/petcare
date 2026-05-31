<script setup>
  import { ref, watch, onMounted, computed } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import DashboardCard from '@/components/shared/DashboardCard.vue';
  import StatusBadge from '@/components/shared/StatusBadge.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { formatDate } from '@/lib/petcare';

  const appStore = useAppStore();

  onMounted(async () => {
    try {
      await Promise.all([
        appStore.fetchAppointmentsToday(),
        appStore.fetchPets(),
      ]);
    } catch (err) {
      console.error('Error fetching clinical data in ClinicalRecords:', err);
    }
  });

  const petIdInput = ref('');
  const medicalRecord = ref(null);
  const vaccineHistory = ref([]);
  const loading = ref(false);

  const formattedMedicalAlerts = computed(() => {
    if (!medicalRecord.value || !medicalRecord.value.medical_alerts) {
      return 'Sin alertas';
    }
    const rawAlerts = medicalRecord.value.medical_alerts;
    if (typeof rawAlerts === 'string' && (rawAlerts.trim().startsWith('[') || rawAlerts.trim().startsWith('{'))) {
      try {
        const parsed = JSON.parse(rawAlerts);
        if (Array.isArray(parsed)) {
          // Si es la lista JSON de consultas, no mostramos el texto plano de todo el JSON.
          // Filtramos diagnósticos o notas críticas si existen, si no, mostramos un mensaje limpio.
          const criticalTerms = ['alergia', 'crítico', 'critico', 'grave', 'urgencia', 'gravedad', 'intoxicación', 'intoxicacion'];
          const criticalAlerts = [];
          parsed.forEach(c => {
            const diagnosis = (c.diagnosis || '').toLowerCase();
            const notes = (c.notes || '').toLowerCase();
            if (criticalTerms.some(term => diagnosis.includes(term) || notes.includes(term))) {
              criticalAlerts.push(`${c.date}: ${c.diagnosis}`);
            }
          });
          
          if (criticalAlerts.length > 0) {
            return criticalAlerts.join(' | ');
          }
          return 'Sin alertas registradas';
        }
      } catch (e) {
        // Fallback
      }
    }
    return rawAlerts;
  });

  async function loadPatientRecord() {
    if (!petIdInput.value) return;
    loading.value = true;
    try {
      const [record, vaccines] = await Promise.all([
        appStore.fetchMedicalRecord(petIdInput.value),
        appStore.fetchVaccinationSchedule(petIdInput.value),
      ]);
      medicalRecord.value = record;
      vaccineHistory.value = vaccines;
    } catch (e) {
      console.error('Error loading patient record:', e);
      medicalRecord.value = null;
      vaccineHistory.value = [];
    } finally {
      loading.value = false;
    }
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Fichas Clínicas"
      subtitle="Historial clínico, vacunas y desparasitaciones por mascota."
    />

    <section class="card" style="padding: 1.5rem;">
      <div class="input-grid" style="align-items: flex-end;">
        <label class="field">
          <span>Seleccionar Paciente (mascota) *</span>
          <select v-model="petIdInput" class="select" required>
            <option value="" disabled>Seleccione un paciente...</option>
            <option v-for="pet in appStore.pets" :key="pet.id" :value="pet.id">
              {{ pet.name }} · {{ pet.breed }} ({{ pet.species === 'dog' ? 'Perro' : pet.species === 'cat' ? 'Gato' : pet.species }})
            </option>
          </select>
        </label>

        <button class="btn btn--primary" type="button" :disabled="loading" @click="loadPatientRecord">
          {{ loading ? 'Cargando...' : 'Buscar ficha' }}
        </button>
      </div>
    </section>

    <div class="stack" v-if="medicalRecord">
      <section class="card">
        <div class="toolbar">
          <div class="toolbar__group">
            <div>
              <h2 class="section__title">{{ medicalRecord.patient_name }}</h2>
              <p class="muted">{{ medicalRecord.species_breed }} · {{ medicalRecord.weight }} kg</p>
            </div>
          </div>
        </div>
      </section>

      <section class="split">
        <DashboardCard title="Información clínica" icon="clipboard-list">
          <div class="stack" style="padding: 0.5rem 0;">
            <div>
              <p class="eyebrow">Alergias</p>
              <p>{{ medicalRecord.allergies || 'Sin alergias registradas' }}</p>
            </div>
            <div>
              <p class="eyebrow">Alertas médicas</p>
              <p>{{ formattedMedicalAlerts }}</p>
            </div>
            <div v-if="medicalRecord.owner_name">
              <p class="eyebrow">Propietario</p>
              <p>{{ medicalRecord.owner_name }} · {{ medicalRecord.owner_email }}</p>
            </div>
          </div>
        </DashboardCard>

        <DashboardCard title="Consultas recientes" icon="stethoscope">
          <div class="list">
            <article
              v-for="(item, index) in (medicalRecord.consultations || [])"
              :key="index"
              class="list__item"
            >
              <div class="list__item-main">
                <p class="list__title">{{ formatDate(item.date) }}</p>
                <p class="list__subtitle">{{ item.diagnosis }}</p>
              </div>
              <StatusBadge status="completed" />
            </article>
            <p v-if="!(medicalRecord.consultations || []).length" class="muted">Sin consultas registradas.</p>
          </div>
        </DashboardCard>
      </section>

      <DashboardCard title="Vacunas y Desparasitaciones" icon="syringe">
        <div class="list">
          <article
            v-for="item in vaccineHistory"
            :key="item.id"
            class="list__item"
          >
            <div class="list__item-main">
              <p class="list__title">{{ item.vaccine_name || item.event_type }}</p>
              <p class="list__subtitle">
                {{ formatDate(item.applied_date) }}
                <span v-if="item.next_due_date"> · Próxima: {{ formatDate(item.next_due_date) }}</span>
              </p>
            </div>
          </article>
          <p v-if="!vaccineHistory.length" class="muted">Sin registros de vacunación.</p>
        </div>
      </DashboardCard>
    </div>

    <p v-if="!medicalRecord && !loading" class="muted" style="text-align: center; padding: 2rem;">
      Seleccione una mascota para cargar su ficha clínica.
    </p>

  </div>
</template>
