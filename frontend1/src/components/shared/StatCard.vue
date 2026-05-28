<script setup>
  import AppIcon from './AppIcon.vue';

  defineProps({
    label: { type: String, required: true },
    value: { type: [String, Number], required: true },
    icon: { type: String, default: 'paw-print' },
    toneClass: { type: String, default: 'chip--brand' },
  });
</script>

<template>
  <article class="card stat-card">
    <div class="stat-card__top">
      <div class="stat-card__icon" :class="toneClass"><AppIcon :name="icon" :size="18" /></div>
      <p class="stat-card__value">{{ value }}</p>
    </div>
    <p class="stat-card__label">{{ label }}</p>
  </article>
</template>
