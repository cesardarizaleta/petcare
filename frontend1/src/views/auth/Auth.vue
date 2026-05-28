<script setup>
  import { useRoute } from 'vue-router';
  import Logo from '@/components/shared/Logo.vue';

  const route = useRoute();
  
  // Opcional: mostrar distintos tips de desarrollo según la ruta
  function getDevTips() {
    return [
      'Cualquier email de dueño registrado funciona.',
      'Usa "vet@test.com" para entrar como Veterinario.',
      'Usa "reception@test.com" para entrar como Recepcionista.',
    ];
  }
</script>

<template>
  <main class="auth-layout">
    <div class="auth-layout__visual">
      <div class="visual-decor visual-decor--1"></div>
      <div class="visual-decor visual-decor--2"></div>
      <div class="auth-layout__visual-content" v-if="route.meta.title">
        <Logo size="lg" />
        <h2 class="visual-title">{{ route.meta.title }}</h2>
        <p class="visual-text" v-if="route.meta.text">{{ route.meta.text }}</p>
        
        <div class="visual-features" v-if="route.meta.features && route.meta.features.length">
          <div class="feature-item" v-for="(feature, idx) in route.meta.features" :key="idx">
            <div class="feature-icon">
              <img :src="feature.icon" :alt="feature.label" class="svg-icon" />
            </div>
            <span>{{ feature.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="auth-layout__form">
      <router-view></router-view>
      
      <div class="dev-note" v-if="route.path === '/login'">
        <p class="dev-note__title"><strong>Tips para desarrollo:</strong></p>
        <ul class="dev-note__list">
          <li v-for="tip in getDevTips()" :key="tip">{{ tip }}</li>
        </ul>
      </div>
    </div>
  </main>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr;
  background: var(--bg);
}

@media (min-width: 1024px) {
  .auth-layout {
    grid-template-columns: 1.2fr 1fr;
  }
}

.auth-layout__visual {
  display: none;
  background: linear-gradient(135deg, rgba(194, 167, 105, 0.05), rgba(165, 186, 142, 0.15)), var(--surface-soft);
  position: relative;
  overflow: hidden;
  border-right: 1px solid var(--border);
}

@media (min-width: 1024px) {
  .auth-layout__visual {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 2.5rem;
  }
}

.visual-decor {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.6;
  z-index: 0;
}

.visual-decor--1 {
  top: -10%;
  left: -10%;
  width: 500px;
  height: 500px;
  background: rgba(194, 167, 105, 0.2);
  animation: float 10s ease-in-out infinite alternate;
}

.visual-decor--2 {
  bottom: -10%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: rgba(165, 186, 142, 0.2);
  animation: float 12s ease-in-out infinite alternate-reverse;
}

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, 50px) scale(1.1); }
}

.auth-layout__visual-content {
  position: relative;
  z-index: 1;
  max-width: 520px;
  margin: 0 auto;
}

.visual-title {
  font-size: clamp(2rem, 3.5vw, 2.5rem);
  margin: 1.5rem 0 1rem;
  line-height: 1.1;
  color: var(--text-strong);
  font-weight: var(--weight-black);
}

.visual-text {
  font-size: 1.1rem;
  color: var(--text);
  opacity: 0.85;
  line-height: 1.5;
  margin-bottom: 2rem;
}

.visual-features {
  display: grid;
  gap: 1rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
}

.feature-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 12px;
  font-size: 1.1rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.svg-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.feature-item span {
  font-weight: var(--weight-bold);
  color: var(--text-strong);
  font-size: 1rem;
}

.auth-layout__form {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 1.5rem;
  position: relative;
  z-index: 1;
  width: 100%;
}

.dev-note {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(165, 186, 142, 0.1);
  border: 1px dashed rgba(165, 186, 142, 0.4);
  border-radius: 12px;
  font-size: 0.8rem;
  max-width: 440px;
  width: 100%;
}

.dev-note__title {
  margin: 0 0 0.5rem;
  color: var(--sage-strong);
}

.dev-note__list {
  margin: 0;
  padding-left: 1.25rem;
  color: rgba(61, 61, 61, 0.7);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
</style>
