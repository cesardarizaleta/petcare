<script setup>
  import { computed } from 'vue';
  import { statusMeta } from '@/lib/petcare';

  const props = defineProps({
    status: { type: String, required: true },
  });

  const meta = computed(
    () => statusMeta[props.status] || { label: props.status, className: 'chip--brand' }
  );
</script>

<template>
  <span class="chip" :class="meta.className">{{ meta.label }}</span>
</template>
