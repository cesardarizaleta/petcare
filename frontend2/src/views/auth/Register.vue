<script setup>
  import { reactive, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import Logo from '@/components/shared/Logo.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();
  const loading = ref(false);

  const form = reactive({
    name: '',
    email: '',
    phone: '',
    address: '',
    dni: '',
    password: '',
  });

  async function handleRegister() {
    if (!form.name || !form.email || !form.password || !form.phone || !form.dni || !form.address) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
      return;
    }

    if (form.dni && !/^[0-9]{6,10}$/.test(form.dni)) {
      toastStore.push({
        title: 'Cédula / DNI inválido',
        description: 'La cédula debe contener entre 6 y 10 dígitos numéricos positivos.',
        type: 'error'
      });
      return;
    }

    if (form.phone && !/^\+?[\d\s\-()]{7,20}$/.test(form.phone)) {
      toastStore.push({
        title: 'Teléfono inválido',
        description: 'El teléfono debe tener un formato válido (entre 7 y 20 caracteres, permitiendo números, espacios, guiones y paréntesis).',
        type: 'error'
      });
      return;
    }

    loading.value = true;
    try {
      await appStore.register(form);
      toastStore.push({
        title: `Bienvenido/a, ${form.name.split(' ')[0]}!`,
        description: 'Tu cuenta fue creada correctamente.',
        type: 'success',
      });
      router.push('/portal/dashboard');
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.email?.[0] || error.response?.data?.error || 'Error al crear la cuenta.';
      toastStore.push({
        title: 'Error de registro',
        description: detail,
        type: 'error',
      });
    } finally {
      loading.value = false;
    }
  }
</script>

<template>
  <main class="auth-screen">
    <section class="auth-card card">
      <div class="auth-card__brand">
        <Logo size="lg" />
        <p class="muted">Sistema de gestión veterinaria PetCare</p>
      </div>

      <div class="section">
        <h1 class="section__title">Crear cuenta</h1>
        <p class="section__subtitle">
          Registrate como propietario de mascotas y comenzá a gestionar turnos.
        </p>
      </div>

      <form class="input-row" @submit.prevent="handleRegister">
        <label class="field">
          <span>Nombre completo</span>
          <input v-model="form.name" class="input" type="text" placeholder="Ana García" />
        </label>

        <div class="input-grid">
          <label class="field">
            <span>Correo electrónico</span>
            <input v-model="form.email" class="input" type="email" placeholder="ana@email.com" />
          </label>
          <label class="field">
            <span>Contraseña</span>
            <input v-model="form.password" class="input" type="password" placeholder="••••••••" />
          </label>
        </div>

        <div class="input-grid">
          <label class="field">
            <span>Teléfono</span>
            <input v-model="form.phone" class="input" type="text" placeholder="555-0000" />
          </label>
          <label class="field">
            <span>Cédula / DNI</span>
            <input v-model="form.dni" class="input" type="text" placeholder="12345678" />
          </label>
        </div>

        <label class="field">
          <span>Dirección</span>
          <input
            v-model="form.address"
            class="input"
            type="text"
            placeholder="Av. Libertad 123"
          />
        </label>

        <button class="btn btn--primary" type="submit" :disabled="loading">
          {{ loading ? 'Creando cuenta...' : 'Crear cuenta' }}
        </button>
      </form>

      <p class="muted" style="margin-top: 1rem; text-align: center;">
        ¿Ya tenés cuenta?
        <router-link to="/login" class="link">Iniciá sesión</router-link>
      </p>
    </section>
  </main>
</template>

<style scoped>
.link {
  color: var(--brand-strong);
  font-weight: var(--weight-bold);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
