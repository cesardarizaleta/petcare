<script setup>
  import { computed } from 'vue';
  import { resolveIcon } from '@/lib/icons';

  const props = defineProps({
    name: { type: String, required: true },
    size: { type: [Number, String], default: 20 },
    strokeWidth: { type: [Number, String], default: 2 },
  });

  const iconComponent = computed(() => resolveIcon(props.name));
</script>

<template>
  <component
    :is="iconComponent"
    class="app-icon"
    :size="size"
    :stroke-width="strokeWidth"
    aria-hidden="true"
    focusable="false"
  />
</template>
