<script setup>
  defineProps({
    title: { type: String, required: true },
    subtitle: { type: String, default: '' },
    accent: { type: String, default: '#C2A769' },
  });
</script>

<template>
  <header class="page-header card">
    <div>
      <div class="page-header__title-row">
        <span class="page-header__accent" :style="{ background: accent }" />
        <h1 class="page-header__title">{{ title }}</h1>
      </div>
      <p v-if="subtitle" class="page-header__subtitle">{{ subtitle }}</p>
    </div>
    <slot name="actions" />
  </header>
</template>
