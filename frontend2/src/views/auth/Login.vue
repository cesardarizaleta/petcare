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
    email: '',
    password: '',
  });

  async function handleLogin() {
    if (!form.email || !form.password) {
      toastStore.push({ title: 'Completa todos los campos', type: 'error' });
      return;
    }

    loading.value = true;
    try {
      const user = await appStore.login(form.email, form.password);
      toastStore.push({
        title: `¡Hola de nuevo, ${user.first_name}!`,
        type: 'success',
      });
      
      const role = appStore.role;
      const redirectMap = {
        owner: '/portal/dashboard',
        vet: '/vet/dashboard',
        receptionist: '/reception/dashboard',
        technician: '/technician/inventory',
        manager: '/manager/dashboard',
      };
      router.push(redirectMap[role] || '/portal/dashboard');
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.detail || error.response?.data?.error || 'Por favor, verifica tu email y contraseña.';
      toastStore.push({
        title: 'Error de inicio de sesión',
        description: detail,
        type: 'error',
      });
    } finally {
      loading.value = false;
    }
  }
</script>

<template>
  <main class="login-screen">
    <section class="login-card card">
      <div class="login-card__brand">
        <Logo size="lg" />
        <p class="muted">Sistema de gestión veterinaria PetCare</p>
      </div>

      <div class="section">
        <h1 class="section__title">Iniciar sesión</h1>
        <p class="section__subtitle">Ingresá tus credenciales para acceder a tu panel.</p>
      </div>

      <form class="input-row" @submit.prevent="handleLogin">
        <label class="field">
          <span>Correo electrónico</span>
          <input v-model="form.email" class="input" type="email" placeholder="ejemplo@email.com" />
        </label>

        <label class="field">
          <span>Contraseña</span>
          <input v-model="form.password" class="input" type="password" placeholder="••••••••" />
        </label>

        <button class="btn btn--primary" type="submit" :disabled="loading">
          {{ loading ? 'Ingresando...' : 'Entrar a mi cuenta' }}
        </button>
      </form>

      <p class="muted" style="margin-top: 1rem; text-align: center;">
        ¿No tienes cuenta?
        <router-link to="/register" class="link">Regístrate aquí</router-link>
      </p>
    </section>
  </main>
</template>

<style scoped>
.login-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: var(--bg);
}

.login-card {
  width: 100%;
  max-width: 480px;
  padding: 2.5rem;
}

.login-card__brand {
  text-align: center;
  margin-bottom: 1.5rem;
}

.link {
  color: var(--brand-strong);
  font-weight: var(--weight-bold);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
