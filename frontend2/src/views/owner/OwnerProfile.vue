<script setup>
  import { reactive, watch, onMounted, ref } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { extractApiError } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const loading = ref(false);

  const form = reactive({
    name: '',
    email: '',
    phone: '',
    address: '',
    dni: '',
  });

  onMounted(async () => {
    try {
      await appStore.fetchProfile();
    } catch (err) {
      console.error('Error fetching owner profile:', err);
    }
  });

  watch(
    () => appStore.currentOwner,
    (owner) => {
      if (!owner) return;
      form.name = owner.name;
      form.email = owner.email;
      form.phone = owner.phone;
      form.address = owner.address;
      form.dni = owner.dni || '';
    },
    { immediate: true }
  );

  async function saveProfile() {
    if (form.dni && !/^[0-9]{6,10}$/.test(form.dni)) {
      toastStore.push({
        title: 'Cédula / DNI inválido',
        description: 'La cédula debe contener entre 6 y 10 dígitos numéricos positivos.',
        type: 'error'
      });
      return;
    }

    loading.value = true;
    try {
      await appStore.updateProfile({
        name: form.name,
        email: form.email,
        phone: form.phone,
        address: form.address,
        dni: form.dni,
      });
      toastStore.push({
        title: 'Perfil actualizado',
        description: 'Los datos del propietario fueron guardados en el servidor.',
        type: 'success',
      });
    } catch (err) {
      console.error(err);
      toastStore.push({
        title: 'Error al guardar perfil',
        description: extractApiError(err, 'No se pudieron actualizar los datos en el servidor.'),
        type: 'error',
      });
    } finally {
      loading.value = false;
    }
  }
</script>

<template>
  <div class="stack">
    <PageHeader
      title="Mi Perfil"
      subtitle="Datos personales del propietario conectado en el demo."
    />

    <section class="card">
      <div class="input-row">
        <div class="input-grid">
          <label class="field"
            ><span>Nombre</span><input v-model="form.name" class="input" type="text"
          /></label>
          <label class="field"
            ><span>Correo electrónico</span><input v-model="form.email" class="input" type="email"
          /></label>
        </div>
        <div class="input-grid">
          <label class="field"
            ><span>Teléfono</span><input v-model="form.phone" class="input" type="text"
          /></label>
          <label class="field"
            ><span>Cédula / DNI</span><input v-model="form.dni" class="input" type="text"
          /></label>
        </div>
        <label class="field"
          ><span>Dirección</span><input v-model="form.address" class="input" type="text"
        /></label>
        <button class="btn btn--primary" type="button" :disabled="loading" @click="saveProfile">
          {{ loading ? 'Guardando cambios...' : 'Guardar cambios' }}
        </button>
      </div>
    </section>
  </div>
</template>

