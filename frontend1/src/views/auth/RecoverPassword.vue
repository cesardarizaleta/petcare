<script setup>
  import { reactive, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import Logo from '@/components/shared/Logo.vue';
  import { useToastStore } from '@/stores/useToastStore';

  const toastStore = useToastStore();
  const router = useRouter();

  const form = reactive({
    email: '',
  });

  const isSubmitted = ref(false);

  function handleRecover() {
    if (!form.email) {
      toastStore.push({ title: 'Ingresa tu correo electrónico', type: 'error' });
      return;
    }

    // Simulamos envío
    setTimeout(() => {
      isSubmitted.value = true;
      toastStore.push({ title: 'Enlace enviado a tu correo', type: 'success' });
    }, 600);
  }
</script>

<template>
  <div class="auth-container card">
    <div class="auth-header">
      <div class="logo-mobile">
        <Logo size="md" />
      </div>
      <h1 class="auth-title">Recuperar contraseña</h1>
      <p class="auth-subtitle" v-if="!isSubmitted">Ingresa tu correo electrónico y te enviaremos instrucciones para restablecer tu contraseña.</p>
      <p class="auth-subtitle" v-else>Hemos enviado un correo a <strong>{{ form.email }}</strong> con instrucciones para recuperar tu contraseña.</p>
    </div>

    <form class="auth-form" @submit.prevent="handleRecover" v-if="!isSubmitted">
      <div class="field">
        <label class="field__label">Correo electrónico</label>
        <div class="input-wrapper">
          <input v-model="form.email" class="input input--auth" type="email" placeholder="ejemplo@email.com" />
        </div>
      </div>

      <button class="btn btn--primary btn--block" type="submit">Enviar instrucciones</button>
    </form>

    <div class="auth-footer" :style="{ marginTop: isSubmitted ? '2rem' : '1.5rem' }">
      <p class="muted">
        <router-link to="/login" class="link" style="margin-left: 0;">Volver al inicio de sesión</router-link>
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
  line-height: 1.5;
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
  width: 100%;
  box-sizing: border-box;
  border: 1px solid transparent;
}

.input--auth:focus {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(194, 167, 105, 0.15);
  outline: none;
  border-color: var(--brand);
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

.field {
  display: flex;
  flex-direction: column;
}

.field__label {
  display: block;
  font-weight: var(--weight-medium);
  margin-bottom: 0.5rem;
  color: var(--text-strong);
}
</style>
