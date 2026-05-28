<script setup>
  import { computed } from 'vue';
  import AppIcon from './AppIcon.vue';
  import { speciesMeta } from '@/lib/petcare';

  const props = defineProps({
    pet: { type: Object, required: true },
    size: { type: String, default: 'md' },
  });

  const meta = computed(() => speciesMeta[props.pet.species] || speciesMeta.other);
  const iconSize = computed(() => ({ sm: 16, md: 20, lg: 24 })[props.size] || 20);
</script>

<template>
  <div class="avatar" :class="[`avatar--${size}`, meta.className]" :title="meta.label">
    <AppIcon class="avatar__icon" :name="meta.icon" :size="iconSize" />
  </div>
</template>
