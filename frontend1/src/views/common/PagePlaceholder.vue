<script setup>
  import PageHeader from '@/components/shared/PageHeader.vue';

  defineProps({
    title: { type: String, required: true },
    subtitle: { type: String, default: '' },
    bullets: { type: Array, default: () => [] },
    tone: { type: String, default: 'brand' },
  });
</script>

<template>
  <div class="page-placeholder stack">
    <PageHeader :title="title" :subtitle="subtitle" />
    <section class="hero-intro">
      <p class="eyebrow">Migración Vue</p>
      <h2 class="hero-intro__title">{{ title }}</h2>
      <p class="hero-intro__text">
        Esta vista ya vive dentro del shell Vue del SDK. El contenido funcional se irá reemplazando
        por la lógica equivalente al frontend React original.
      </p>
      <div class="toolbar">
        <span class="chip" :class="`chip--${tone}`">Plantilla activa</span>
      </div>
    </section>
    <section class="card">
      <h3 class="section__title">Qué sigue en esta pantalla</h3>
      <ul class="page-placeholder__list">
        <li v-for="bullet in bullets" :key="bullet">{{ bullet }}</li>
      </ul>
    </section>
  </div>
</template>
