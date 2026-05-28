<script setup>
  import AppIcon from './AppIcon.vue';

  defineProps({
    title: { type: String, required: true },
    icon: { type: String, default: 'clipboard-list' },
    actionLabel: { type: String, default: '' },
  });

  defineEmits(['action']);
</script>

<template>
  <section class="card">
    <div class="dashboard-card__header">
      <h2 class="dashboard-card__title">
        <span class="dashboard-card__icon"><AppIcon :name="icon" :size="18" /></span>{{ title }}
      </h2>
      <button
        v-if="actionLabel"
        class="dashboard-card__action"
        type="button"
        @click="$emit('action')"
      >
        {{ actionLabel }}
      </button>
    </div>
    <slot />
  </section>
</template>
