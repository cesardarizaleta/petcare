<script setup>
  import { reactive } from 'vue';
  import { useRouter } from 'vue-router';
  import Logo from '@/components/shared/Logo.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();

  const form = reactive({
    email: '',
    password: '',
  });

  async function handleLogin() {
    if (!form.email || !form.password) {
      toastStore.push({ title: 'Completa todos los campos', type: 'error' });
      return;
    }

    try {
      const user = await appStore.login(form.email, form.password);
      toastStore.push({
        title: `¡Hola de nuevo, ${user.first_name}!`,
        type: 'success',
      });
      
      const role = appStore.role;
      if (role === 'owner') {
        router.push('/portal/dashboard');
      } else if (role === 'vet') {
        router.push('/vet/dashboard');
      } else if (role === 'receptionist') {
        router.push('/reception/dashboard');
      }
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.detail || error.response?.data?.error || 'Por favor, verifica tu email y contraseña.';
      toastStore.push({
        title: 'Error de inicio de sesión',
        description: detail,
        type: 'error',
      });
    }
  }
</script>

<template>
  <div class="auth-container card">
    <div class="auth-header">
      <div class="logo-mobile">
        <Logo size="md" />
      </div>
      <h1 class="auth-title">Iniciar sesión</h1>
      <p class="auth-subtitle">Ingresá tus credenciales para acceder a tu panel.</p>
    </div>

    <form class="auth-form" @submit.prevent="handleLogin">
      <div class="field">
        <label class="field__label">Correo electrónico</label>
        <div class="input-wrapper">
          <input v-model="form.email" class="input input--auth" type="email" placeholder="ejemplo@email.com" />
        </div>
      </div>
      
      <div class="field">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <label class="field__label" style="margin-bottom: 0;">Contraseña</label>
          <router-link to="/recover-password" class="link" style="font-size: 0.85rem; font-weight: normal;">¿Olvidaste tu contraseña?</router-link>
        </div>
        <div class="input-wrapper">
          <input v-model="form.password" class="input input--auth" type="password" placeholder="••••••••" />
        </div>
      </div>

      <button class="btn btn--primary btn--block" type="submit">Entrar a mi cuenta</button>
    </form>

    <div class="auth-footer">
      <p class="muted">¿No tienes una cuenta? 
        <router-link to="/register" class="link">Regístrate aquí</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>

.auth-container {
  width: 100%;
  max-width: 440px;
  padding: 2rem;
  border-radius: 24px;
  background: var(--surface);
  box-shadow: var(--shadow);
}

.auth-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.logo-mobile {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

@media (min-width: 1024px) {
  .logo-mobile {
    display: none;
  }
}

.auth-title {
  font-size: 1.8rem;
  font-weight: var(--weight-black);
  color: var(--text-strong);
  margin-bottom: 0.25rem;
}

.auth-subtitle {
  color: var(--text);
  opacity: 0.7;
  font-size: 0.95rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input--auth {
  padding: 0.85rem 1rem;
  font-size: 1rem;
  border-radius: 14px;
  background: #fff;
  transition: all 0.2s ease;
}

.input--auth:focus {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(194, 167, 105, 0.15);
}

.btn--block {
  width: 100%;
  justify-content: center;
  padding: 0.85rem;
  font-size: 1.05rem;
  margin-top: 0.5rem;
  border-radius: 14px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: 0 4px 15px rgba(194, 167, 105, 0.3);
}

.btn--block:hover {
  box-shadow: 0 6px 20px rgba(194, 167, 105, 0.4);
}

.auth-footer {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.95rem;
}

.link {
  color: var(--brand-strong);
  font-weight: var(--weight-bold);
  text-decoration: none;
  transition: all 0.2s ease;
  margin-left: 0.25rem;
}

.link:hover {
  color: var(--brand);
  text-decoration: underline;
}


</style>
