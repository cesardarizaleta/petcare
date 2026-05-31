<script setup>
  import { reactive } from 'vue';
  import { useRouter } from 'vue-router';
  import Logo from '@/components/shared/Logo.vue';
  import { useAppStore } from '@/stores/useAppStore';
  import { useToastStore } from '@/stores/useToastStore';
  import { getTodayShortDate } from '@/lib/petcare';

  const appStore = useAppStore();
  const toastStore = useToastStore();
  const router = useRouter();

  const form = reactive({
    name: '',
    email: '',
    phone: '',
    address: '',
    dni: '',
    password: '',
  });

  async function handleRegister() {
    if (!form.name || !form.email || !form.password) {
      toastStore.push({ title: 'Completa los campos requeridos', type: 'error' });
      return;
    }

    try {
      await appStore.register({
        name: form.name,
        email: form.email,
        password: form.password,
        phone: form.phone,
        address: form.address,
        dni: form.dni,
      });

      toastStore.push({
        title: `Bienvenido/a, ${form.name.split(' ')[0]}!`,
        description: 'Tu cuenta fue creada correctamente.',
        type: 'success',
      });
      router.push('/portal/dashboard');
    } catch (error) {
      console.error(error);
      const errors = error.response?.data;
      let msg = 'Hubo un problema al crear tu cuenta.';
      if (errors && typeof errors === 'object') {
        const firstKey = Object.keys(errors)[0];
        const val = errors[firstKey];
        msg = Array.isArray(val) ? `${firstKey}: ${val[0]}` : `${firstKey}: ${val}`;
      }
      toastStore.push({
        title: 'Error de registro',
        description: msg,
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
      <h1 class="auth-title">Crear cuenta</h1>
      <p class="auth-subtitle">Registrate como propietario y comenzá a gestionar turnos.</p>
    </div>

    <form class="auth-form" @submit.prevent="handleRegister">
      <div class="field">
        <label class="field__label">Nombre completo *</label>
        <input v-model="form.name" class="input input--auth" type="text" placeholder="Ana García" />
      </div>

      <div class="input-grid">
        <div class="field">
          <label class="field__label">Correo electrónico *</label>
          <input v-model="form.email" class="input input--auth" type="email" placeholder="ana@email.com" />
        </div>
        <div class="field">
          <label class="field__label">Contraseña *</label>
          <input v-model="form.password" class="input input--auth" type="password" placeholder="••••••••" />
        </div>
      </div>

      <div class="input-grid">
        <div class="field">
          <label class="field__label">Teléfono</label>
          <input v-model="form.phone" class="input input--auth" type="text" placeholder="555-0000" />
        </div>
        <div class="field">
          <label class="field__label">Cédula / DNI</label>
          <input v-model="form.dni" class="input input--auth" type="text" placeholder="12345678" />
        </div>
      </div>

      <div class="field">
        <label class="field__label">Dirección</label>
        <input v-model="form.address" class="input input--auth" type="text" placeholder="Av. Libertad 123" />
      </div>

      <button class="btn btn--primary btn--block" type="submit">Crear cuenta</button>
    </form>

    <p class="terms muted">Al registrarte aceptas los términos y condiciones de PetCare.</p>

    <div class="auth-footer">
      <p class="muted">¿Ya tienes cuenta? 
        <router-link to="/login" class="link">Inicia sesión</router-link>
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

.terms {
  text-align: center;
  font-size: 0.8rem;
  margin-top: 1rem;
}
</style>
