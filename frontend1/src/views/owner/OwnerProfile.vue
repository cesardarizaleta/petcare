<script setup>
  import { reactive, watch, onMounted } from 'vue';
  import PageHeader from '@/components/shared/PageHeader.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';

  const appStore = useAppStore();
  const toastStore = useToastStore();

  const form = reactive({
    name: '',
    email: '',
    phone: '',
    address: '',
  });

  onMounted(() => {
    appStore.fetchProfile().catch((err) => console.error(err));
  });

  watch(
    () => appStore.currentOwner,
    (owner) => {
      if (!owner) return;
      form.name = owner.name;
      form.email = owner.email;
      form.phone = owner.phone;
      form.address = owner.address;
    },
    { immediate: true }
  );

  async function saveProfile() {
    try {
      await appStore.updateProfile({
        name: form.name,
        phone: form.phone,
        address: form.address,
      });
      toastStore.push({
        title: 'Perfil actualizado',
        description: 'Los datos del propietario fueron guardados.',
        type: 'success',
      });
    } catch (error) {
      console.error(error);
      toastStore.push({
        title: 'Error al guardar cambios',
        description: 'No se pudieron actualizar los datos del perfil.',
        type: 'error',
      });
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
            ><span>Dirección</span><input v-model="form.address" class="input" type="text"
          /></label>
        </div>
        <button class="btn btn--primary" type="button" @click="saveProfile">Guardar cambios</button>
      </div>
    </section>
  </div>
</template>
